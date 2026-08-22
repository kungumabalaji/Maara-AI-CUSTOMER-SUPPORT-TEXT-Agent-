# Resend wrapper (build if not done yet)
from services import notification_service
from services import confirmation_store
from services import rag_service        # your existing RAG
from langchain_groq import ChatGroq
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph, START, END
import os
import operator
import re
import traceback
from typing import TypedDict, Annotated

from dotenv import load_dotenv
load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")

llm = ChatGroq(model="openai/gpt-oss-120b", api_key=GROQ_API_KEY)
confirmation_store.init_table()


# ------------------------------------------------------------
# STATE — everything that flows through the graph
# ------------------------------------------------------------
class RepairAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    thread_id: str
    user_query: str
    faq_answer: str | None          # set if RAG had a real answer
    is_problem_report: bool          # true if this looks like a repair issue, not an FAQ
    diagnostic_answers: dict         # accumulated answers to technician-style questions
    diagnosis_complete: bool
    repair_summary: str | None       # final LLM-written summary once diagnosis is done
    customer_email: str | None
    llm_calls: int


# ------------------------------------------------------------
# NODE 1 — understand_query
# Decides: is this an FAQ-style question, or a "my device is broken" report?
# ------------------------------------------------------------
def understand_query_node(state: RepairAgentState) -> dict:
    query = state["user_query"]

    classification_prompt = f"""Classify this customer message as either:
- "faq" — a general question about policy, pricing, hours, warranty, supported devices
- "problem" — the customer is describing something wrong with their own device

Message: "{query}"

Reply with exactly one word: faq or problem"""

    response = llm.invoke([HumanMessage(content=classification_prompt)])
    label = response.content.strip().lower()

    return {
        "is_problem_report": label == "problem",
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# ------------------------------------------------------------
# NODE 2 — faq_node
# Only runs for FAQ-style questions. Searches RAG, answers from it,
# never invents an answer if RAG comes back empty.
# ------------------------------------------------------------
def faq_node(state: RepairAgentState) -> dict:
    query = state["user_query"]
    results = rag_service.search(query, top_k=5)

    if not results:
        answer = "I don't have that information on file — I'll flag this for our team to confirm."
    else:
        context = "\n".join(r["content"] for r in results)
        answer_prompt = f"""Answer the customer's question using ONLY this context.
If the context doesn't contain the answer, say you're not sure.

Context:
{context}

Question: {query}"""
        response = llm.invoke([HumanMessage(content=answer_prompt)])
        answer = response.content

    return {
        "faq_answer": answer,
        "messages": [AIMessage(content=answer)],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# ------------------------------------------------------------
# NODE 3 — diagnostic_node
# This is the piece you specifically asked about: technician-style
# follow-up questions, NOT customer-facing FAQ. Asks one question at
# a time (when did it start, did you drop it, does it happen every
# time, etc.) and keeps looping until it has enough to summarize.
# ------------------------------------------------------------
DIAGNOSTIC_SYSTEM_PROMPT = """You are gathering repair intake information,
the way a technician would when a device is dropped off. Ask ONE focused
diagnostic question at a time based on what's already been said — e.g.
when the issue started, whether the device was dropped or got wet, whether
the problem happens every time or intermittently, what troubleshooting the
customer has already tried.

Do NOT give repair advice or attempt to fix anything yourself — you are
only collecting information for the technician.

Once you have the device model, the specific fault, when it started, and
whether there's a likely cause (drop/liquid/wear), ask ONE more question:
whether they'd like an on-site repair (a technician visits their location)
or a shop repair (they bring the device to the shop).

- If they choose on-site, ask for their address next (it's required).
- If they choose shop, no address is needed.

Finally, ask for the customer's email address if it hasn't been given yet
(it's required before you can finish).

Once you have ALL of: device model, fault, when it started, likely cause,
repair mode (on-site or shop) with address if on-site, and the customer's
email address, respond with exactly "DIAGNOSIS_COMPLETE" as the first word
of your reply, followed by a short plain-text summary of everything
gathered — including the repair mode, address if applicable, and the email
address."""

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


def _extract_email(messages: list[AnyMessage]) -> str | None:
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            match = EMAIL_RE.search(message.content)
            if match:
                return match.group(0)
    return None


def diagnostic_node(state: RepairAgentState) -> dict:
    history = state["messages"]
    response = llm.invoke(
        [SystemMessage(content=DIAGNOSTIC_SYSTEM_PROMPT), *history])
    content = response.content

    if content.startswith("DIAGNOSIS_COMPLETE"):
        summary_text = content.replace("DIAGNOSIS_COMPLETE", "", 1).strip()
        customer_email = _extract_email(history)

        if not customer_email:
            # No email captured yet — ask for it instead of finishing.
            return {
                "diagnosis_complete": False,
                "messages": [AIMessage(
                    content="Before I finalize this, could you share your email address so we can send you a confirmation?"
                )],
                "llm_calls": state.get("llm_calls", 0) + 1,
            }

        return {
            "diagnosis_complete": True,
            "repair_summary": summary_text,
            "customer_email": customer_email,
            "messages": [AIMessage(content=summary_text)],
            "llm_calls": state.get("llm_calls", 0) + 1,
        }

    # Not done yet — ask the next diagnostic question, loop continues
    return {
        "diagnosis_complete": False,
        "messages": [AIMessage(content=content)],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# ------------------------------------------------------------
# NODE 4 — service_node
# Runs once diagnosis is complete. Takes the confirmed summary and
# emails it via Resend — to the customer (confirmation) and the
# owner (repair intake summary), exactly what you described.
# ------------------------------------------------------------
def service_node(state: RepairAgentState) -> dict:
    summary = state["repair_summary"]
    customer_email = state.get("customer_email")
    thread_id = state["thread_id"]

    try:
        token = confirmation_store.create_confirmation(
            thread_id=thread_id,
            customer_email=customer_email,
            summary=summary,
        )
        dashboard_url = f"{FRONTEND_BASE_URL}/?view=dashboard&token={token}"
        notification_service.send_owner_alert_email(summary=summary, dashboard_url=dashboard_url)
    except Exception:
        print("ERROR: failed to send owner alert email")
        traceback.print_exc()

    confirmation = (
        "Thanks — I've sent your details to our team. You'll get a confirmation "
        "email as soon as the repair time is approved."
    )
    return {
        "messages": [AIMessage(content=confirmation)],
    }


# ------------------------------------------------------------
# ROUTING — decides which path a turn takes
# ------------------------------------------------------------
def route_from_start(state: RepairAgentState) -> str:
    # Already mid-diagnostic on a prior turn? Skip re-classification —
    # a bare follow-up reply (an address, "yes", a device model) doesn't
    # read as a "problem report" on its own and would get misrouted to faq.
    if state.get("is_problem_report") and not state.get("diagnosis_complete"):
        return "diagnostic"
    return "understand_query"


def route_after_understanding(state: RepairAgentState) -> str:
    return "diagnostic" if state["is_problem_report"] else "faq"


def route_after_diagnostic(state: RepairAgentState) -> str:
    return "service" if state.get("diagnosis_complete") else END


# ------------------------------------------------------------
# GRAPH ASSEMBLY
# ------------------------------------------------------------
graph = StateGraph(RepairAgentState)

graph.add_node("understand_query", understand_query_node)
graph.add_node("faq", faq_node)
graph.add_node("diagnostic", diagnostic_node)
graph.add_node("service", service_node)

graph.add_conditional_edges(
    START,
    route_from_start,
    {"understand_query": "understand_query", "diagnostic": "diagnostic"},
)
graph.add_conditional_edges(
    "understand_query",
    route_after_understanding,
    {"faq": "faq", "diagnostic": "diagnostic"},
)
graph.add_edge("faq", END)
graph.add_conditional_edges(
    "diagnostic",
    route_after_diagnostic,
    {"service": "service", END: END},
)
graph.add_edge("service", END)


def build_app(checkpointer):
    return graph.compile(checkpointer=checkpointer)


# ------------------------------------------------------------
# ENTRYPOINT — what main.py calls
# ------------------------------------------------------------
def run_repair_agent(user_input: str, thread_id: str | None = None) -> dict:
    import uuid
    thread_id = thread_id or str(uuid.uuid4())

    with PostgresSaver.from_conn_string(os.getenv("DATABASE_URL")) as checkpointer:
        checkpointer.setup()
        app = build_app(checkpointer)
        config = {"configurable": {"thread_id": thread_id}}

        is_new_thread = not app.get_state(config).values

        if is_new_thread:
            turn_input = {
                "messages": [HumanMessage(content=user_input)],
                "thread_id": thread_id,
                "user_query": user_input,
                "faq_answer": None,
                "is_problem_report": False,
                "diagnostic_answers": {},
                "diagnosis_complete": False,
                "repair_summary": None,
                "customer_email": None,
                "llm_calls": 0,
            }
        else:
            # Don't reset accumulated flags (is_problem_report, etc.) on
            # follow-up turns — only add the new message, so routing can
            # tell we're still mid-diagnostic. See route_from_start.
            turn_input = {
                "messages": [HumanMessage(content=user_input)],
                "user_query": user_input,
            }

        result = app.invoke(turn_input, config=config)

        return {
            "thread_id": thread_id,
            "answer": result["messages"][-1].content,
            "llm_calls": result["llm_calls"],
        }
