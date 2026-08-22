import os
import secrets

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
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )


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


def confirm_token(token: str) -> dict | None:
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
            "UPDATE repair_confirmations SET confirmed = TRUE WHERE token = %s",
            (token,),
        )
        return {"customer_email": customer_email, "summary": summary, "already_confirmed": False}
