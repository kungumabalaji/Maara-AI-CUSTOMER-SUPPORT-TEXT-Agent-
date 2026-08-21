import os
from functools import lru_cache

from groq import Groq

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
DEFAULT_SYSTEM_PROMPT = os.getenv(
    "CHATBOT_SYSTEM_PROMPT",
    "You are a helpful, concise customer support assistant. Answer only using the "
    "provided knowledge base context below. If the context does not confidently "
    "answer the question, say so and suggest connecting the customer with a human agent.",
)


@lru_cache(maxsize=1)
def _client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set in the backend environment.")
    return Groq(api_key=api_key)


def answer_from_context(question: str, context_chunks: list[str]) -> str:
    context = "\n\n---\n\n".join(context_chunks) or "No matching context found."

    completion = _client().chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Knowledge base context:\n{context}\n\nCustomer question: {question}",
            },
        ],
        temperature=0.3,
    )
    return completion.choices[0].message.content or ""
