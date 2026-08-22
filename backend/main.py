import traceback
from datetime import datetime

import uvicorn

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.agents.repair_agents import run_repair_agent
from services import auth_service
from services import confirmation_store
from services import notification_service

auth_service.init_tables()

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


class SignupRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class ScheduleRequest(BaseModel):
    scheduled_at: str
    technician: str
    notes: str = ""


def current_owner_id(authorization: str | None = Header(default=None)) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header.")

    token = authorization.removeprefix("Bearer ").strip()
    owner_id = auth_service.get_owner_from_token(token)

    if owner_id is None:
        raise HTTPException(status_code=401, detail="Session expired or invalid — please log in again.")

    return owner_id


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


@app.get("/api/auth/needs-setup")
def auth_needs_setup():
    return {"needs_setup": auth_service.owner_count() == 0}


@app.post("/api/auth/signup")
def signup(signup_request: SignupRequest, authorization: str | None = Header(default=None)):
    # Open only for the very first owner account; afterwards, only an
    # already-logged-in owner can create additional staff accounts.
    if auth_service.owner_count() > 0:
        current_owner_id(authorization)

    try:
        owner_id = auth_service.create_owner(signup_request.email, signup_request.password)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    token = auth_service.create_session(owner_id)
    return {"token": token, "email": signup_request.email.lower()}


@app.post("/api/auth/login")
def login(login_request: LoginRequest):
    owner_id = auth_service.authenticate(login_request.email, login_request.password)

    if owner_id is None:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = auth_service.create_session(owner_id)
    return {"token": token, "email": login_request.email.lower()}


@app.get("/api/repair/pending")
def repair_pending(owner_id: int = Depends(current_owner_id)):
    return {"pending": confirmation_store.list_pending()}


@app.post("/api/repair/schedule/{token}")
def repair_schedule(token: str, schedule_request: ScheduleRequest, owner_id: int = Depends(current_owner_id)):
    try:
        scheduled_at = datetime.fromisoformat(schedule_request.scheduled_at)
    except ValueError:
        raise HTTPException(status_code=400, detail="scheduled_at must be an ISO datetime string.")

    result = confirmation_store.schedule_and_confirm(
        token=token,
        scheduled_at=scheduled_at,
        technician=schedule_request.technician,
        notes=schedule_request.notes,
    )

    if result is None:
        raise HTTPException(status_code=404, detail="No pending repair found for this token.")

    if result["already_confirmed"]:
        raise HTTPException(status_code=409, detail="This repair was already confirmed.")

    try:
        notification_service.send_customer_confirmed_email(
            customer_email=result["customer_email"],
            summary=result["summary"],
            scheduled_at=schedule_request.scheduled_at,
            technician=schedule_request.technician,
            notes=schedule_request.notes,
        )
    except Exception:
        print("ERROR: failed to send customer confirmed email")
        traceback.print_exc()

    return {"success": True}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Enable auto-reload for development
    )
