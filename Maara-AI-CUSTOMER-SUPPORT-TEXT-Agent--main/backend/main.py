import traceback
import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.agents.repair_agents import run_repair_agent
from services import confirmation_store
from services import notification_service

app = FastAPI(
    title="Maara AI Customer Support Text Agent",
    description="A customer support text agent that uses RAG to answer customer questions.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RepairRequest(BaseModel):
    message: str
    thread_id: str | None = None


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/repair")
async def repair(repair_request: RepairRequest):
    try:
        user_message = repair_request.message.strip()

        if not user_message:
            return JSONResponse(
                status_code=400,
                content={"error": "Message cannot be empty."},
            )

        result = run_repair_agent(
            user_input=user_message,
            thread_id=repair_request.thread_id,
        )

        return JSONResponse(
            content={
                "success": True,
                "thread_id": result["thread_id"],
                "answer": result["answer"],
            }
        )

    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
            },
        )


@app.get("/api/repair/confirm/{token}", response_class=HTMLResponse)
def confirm_repair(token: str):
    result = confirmation_store.confirm_token(token)

    if result is None:
        return HTMLResponse("<h2>This confirmation link is invalid.</h2>", status_code=404)

    if result["already_confirmed"]:
        return HTMLResponse("<h2>This repair was already confirmed.</h2>")

    try:
        notification_service.send_customer_confirmed_email(
            customer_email=result["customer_email"],
            summary=result["summary"],
        )
    except Exception:
        print("ERROR: failed to send customer confirmed email")
        traceback.print_exc()

    return HTMLResponse("<h2>Repair confirmed! The customer has been notified.</h2>")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Enable auto-reload for development
    )
