import os
import secrets
from datetime import datetime

import psycopg


def _conn():
    return psycopg.connect(os.getenv("DATABASE_URL"))


def init_table() -> None:
    with _conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS repair_confirmations (
                token TEXT PRIMARY KEY,
                thread_id TEXT NOT NULL,
                customer_email TEXT NOT NULL,
                summary TEXT NOT NULL,
                confirmed BOOLEAN NOT NULL DEFAULT FALSE,
                scheduled_at TIMESTAMPTZ,
                technician TEXT,
                notes TEXT,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        conn.execute("ALTER TABLE repair_confirmations ADD COLUMN IF NOT EXISTS scheduled_at TIMESTAMPTZ")
        conn.execute("ALTER TABLE repair_confirmations ADD COLUMN IF NOT EXISTS technician TEXT")
        conn.execute("ALTER TABLE repair_confirmations ADD COLUMN IF NOT EXISTS notes TEXT")


def create_confirmation(thread_id: str, customer_email: str, summary: str) -> str:
    token = secrets.token_urlsafe(32)
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO repair_confirmations (token, thread_id, customer_email, summary)
            VALUES (%s, %s, %s, %s)
            """,
            (token, thread_id, customer_email, summary),
        )
    return token


def list_pending() -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            """
            SELECT token, thread_id, customer_email, summary, created_at
            FROM repair_confirmations
            WHERE confirmed = FALSE
            ORDER BY created_at ASC
            """
        ).fetchall()

    return [
        {
            "token": token,
            "thread_id": thread_id,
            "customer_email": customer_email,
            "summary": summary,
            "created_at": created_at.isoformat(),
        }
        for token, thread_id, customer_email, summary, created_at in rows
    ]


def schedule_and_confirm(
    token: str, scheduled_at: datetime, technician: str, notes: str
) -> dict | None:
    with _conn() as conn:
        row = conn.execute(
            "SELECT customer_email, summary, confirmed FROM repair_confirmations WHERE token = %s",
            (token,),
        ).fetchone()

        if row is None:
            return None

        customer_email, summary, confirmed = row

        if confirmed:
            return {"customer_email": customer_email, "summary": summary, "already_confirmed": True}

        conn.execute(
            """
            UPDATE repair_confirmations
            SET confirmed = TRUE, scheduled_at = %s, technician = %s, notes = %s
            WHERE token = %s
            """,
            (scheduled_at, technician, notes, token),
        )
        return {
            "customer_email": customer_email,
            "summary": summary,
            "scheduled_at": scheduled_at,
            "technician": technician,
            "notes": notes,
            "already_confirmed": False,
        }
