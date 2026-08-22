import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

import psycopg
import psycopg.errors

SESSION_LIFETIME = timedelta(days=7)


def _conn():
    return psycopg.connect(os.getenv("DATABASE_URL"))


def init_tables() -> None:
    with _conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS owners (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS owner_sessions (
                token TEXT PRIMARY KEY,
                owner_id INTEGER NOT NULL REFERENCES owners(id),
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                expires_at TIMESTAMPTZ NOT NULL
            )
            """
        )


def _hash_password(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000).hex()


def owner_count() -> int:
    with _conn() as conn:
        return conn.execute("SELECT count(*) FROM owners").fetchone()[0]


def create_owner(email: str, password: str) -> int:
    salt = secrets.token_bytes(16)
    password_hash = _hash_password(password, salt)

    with _conn() as conn:
        try:
            row = conn.execute(
                "INSERT INTO owners (email, password_hash, salt) VALUES (%s, %s, %s) RETURNING id",
                (email.lower(), password_hash, salt.hex()),
            ).fetchone()
        except psycopg.errors.UniqueViolation:
            raise ValueError("An account with this email already exists.")
        return row[0]


def authenticate(email: str, password: str) -> int | None:
    with _conn() as conn:
        row = conn.execute(
            "SELECT id, password_hash, salt FROM owners WHERE email = %s",
            (email.lower(),),
        ).fetchone()

    if row is None:
        return None

    owner_id, password_hash, salt_hex = row
    if _hash_password(password, bytes.fromhex(salt_hex)) != password_hash:
        return None

    return owner_id


def create_session(owner_id: int) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + SESSION_LIFETIME

    with _conn() as conn:
        conn.execute(
            "INSERT INTO owner_sessions (token, owner_id, expires_at) VALUES (%s, %s, %s)",
            (token, owner_id, expires_at),
        )
    return token


def get_owner_from_token(token: str) -> int | None:
    with _conn() as conn:
        row = conn.execute(
            "SELECT owner_id, expires_at FROM owner_sessions WHERE token = %s",
            (token,),
        ).fetchone()

    if row is None:
        return None

    owner_id, expires_at = row
    if expires_at < datetime.now(timezone.utc):
        return None

    return owner_id
