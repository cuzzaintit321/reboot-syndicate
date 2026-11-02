"""Reboot Syndicate consultation notifications via Resend."""
import json
import logging
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

logger = logging.getLogger("reboot.notifications")


def send_consultation_alert(lead: dict) -> bool:
    key = os.getenv("RESEND_API_KEY", "").strip()
    recipient = os.getenv("NOTIFY_TO", "").strip()
    sender = os.getenv(
        "RESEND_FROM", "notifications@rebootsyndicate.com"
    ).strip()

    if not key or not recipient:
        logger.error("Resend notification skipped: missing configuration")
        return False

    service = " ".join(str(lead["service"]).split())[:75]
    message = (
        "NEW REBOOT SYNDICATE CONSULTATION\n"
        "================================\n"
        f"Request ID: {lead['id']}\n"
        f"Date (UTC): {lead['created_at']}\n"
        f"Name: {lead['name']}\n"
        f"Email: {lead['email']}\n"
        f"Phone: {lead.get('phone') or 'Not provided'}\n"
        f"Service: {service}\n\n"
        "PROJECT DETAILS\n"
        "---------------\n"
        f"{lead['message']}\n\n"
        "This inquiry is also saved on the website server.\n"
    )

    payload = {
        "from": f"Reboot Syndicate <{sender}>",
        "to": [recipient],
        "subject": f"[Reboot Syndicate] New request #{lead['id']} - {service}",
        "text": message,
        "reply_to": str(lead["email"]).strip(),
    }

    request = Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "RebootSyndicate/1.0",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=15) as response:
            if response.status not in (200, 201):
                logger.error("Resend unexpected HTTP status: %s", response.status)
                return False
        logger.info("Resend notification accepted for request #%s", lead["id"])
        return True
    except HTTPError as exc:
        logger.error("Resend rejected request #%s: HTTP %s", lead["id"], exc.code)
    except (URLError, OSError, ValueError) as exc:
        logger.error(
            "Resend notification failed for request #%s (%s)",
            lead["id"], type(exc).__name__
        )
    return False
