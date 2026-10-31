"""Email alerts for consultation requests.

The form saves every request in SQLite first. Email is a best-effort notification;
SMTP failures must never discard the saved customer inquiry.
Credentials and the recipient come exclusively from environment variables.
"""
import logging
import os
import smtplib
import ssl
from email.message import EmailMessage

logger = logging.getLogger("reboot.notifications")


def send_consultation_alert(lead: dict) -> None:
    """Send one alert through an authenticated TLS/SSL SMTP connection.

    Designed for FastAPI BackgroundTasks, after the database transaction commits.
    Intentionally does not log customer data or SMTP secrets on failure.
    """
    recipient = os.getenv("NOTIFY_TO", "").strip()
    username = os.getenv("SMTP_USERNAME", "").strip()
    password = os.getenv("SMTP_APP_PASSWORD", "").replace(" ", "").strip()
    if not (recipient and username and password):
        logger.warning("Consultation notification skipped: email settings not configured")
        return

    host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    subject_service = " ".join(str(lead["service"]).split())[:75]

    message = EmailMessage()
    message["Subject"] = f"[Reboot Syndicate] New request #{lead['id']} - {subject_service}"
    message["From"] = username
    message["To"] = recipient
    # The form verifies the customer's email address; reply directly to them.
    message["Reply-To"] = str(lead["email"])
    message.set_content(
        "NEW REBOOT SYNDICATE CONSULTATION\n"
        "================================\n"
        f"Request ID: {lead['id']}\n"
        f"Date (UTC): {lead['created_at']}\n"
        f"Name: {lead['name']}\n"
        f"Email: {lead['email']}\n"
        f"Phone: {lead['phone'] or 'Not provided'}\n"
        f"Service: {lead['service']}\n\n"
        "PROJECT DETAILS\n"
        "---------------\n"
        f"{lead['message']}\n\n"
        "This is an automated notification. The inquiry is saved on your server.\n"
        "Reply to this email to contact the customer directly.\n"
    )

    try:
        port = int(os.getenv("SMTP_PORT", "465"))
        with smtplib.SMTP_SSL(host, port, timeout=12, context=ssl.create_default_context()) as smtp:
            smtp.login(username, password)
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException, ValueError) as exc:
        logger.error("Consultation email notification failed for request #%s (%s)", lead["id"], type(exc).__name__)
    else:
        logger.info("Consultation email notification sent for request #%s", lead["id"])
