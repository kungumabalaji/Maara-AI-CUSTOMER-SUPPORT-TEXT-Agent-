import os

import resend

resend.api_key = os.getenv("RESEND_API_KEY")

FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "support@example.com")
OWNER_EMAIL = os.getenv("RESEND_OWNER_EMAIL")


def send_owner_alert_email(summary: str, dashboard_url: str) -> None:
    if not OWNER_EMAIL:
        return

    resend.Emails.send(
        {
            "from": FROM_EMAIL,
            "to": [OWNER_EMAIL],
            "subject": "New repair intake — schedule needed",
            "text": (
                "A new repair intake was collected:\n\n"
                f"{summary}\n\n"
                "Log in to the dashboard to review and schedule this repair — "
                "the customer will be notified once you do:\n"
                f"{dashboard_url}"
            ),
        }
    )


def send_customer_confirmed_email(
    customer_email: str,
    summary: str,
    scheduled_at: str,
    technician: str,
    notes: str,
) -> None:
    if not customer_email:
        return

    details = f"Scheduled for: {scheduled_at}\nTechnician: {technician}"
    if notes:
        details += f"\nNotes: {notes}"

    resend.Emails.send(
        {
            "from": FROM_EMAIL,
            "to": [customer_email],
            "subject": "Your repair appointment is confirmed",
            "text": (
                "Good news — the shop owner has confirmed your repair appointment.\n\n"
                f"{summary}\n\n"
                f"{details}\n\n"
                "We'll be in touch with any further details. Thanks for choosing us!"
            ),
        }
    )
