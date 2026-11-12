"""Stripe-hosted checkout. No card data is handled by this application."""
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import stripe
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse

router = APIRouter()
DB = Path(os.getenv("DATABASE_PATH", "/data/requests.sqlite3"))
# Fixed server-side prices; never accept an amount from the browser.
CATALOG = {
    "website-business": ("Business Website - up to 5 pages", 69900, "payment"),
    "website-premium": ("Premium Website - up to 10 pages", 129900, "payment"),
    "website-care": ("Website Care", 4900, "subscription"),
    "website-design": ("Website Design", 29900, "payment"),
    "local-seo": ("Search Engine Optimization", 24900, "subscription"),
    "google-business-profile": ("Google Business Profile", 9900, "payment"),
    "social-media": ("Social Media Management", 29900, "subscription"),
    "digital-advertising": ("Paid Advertising Management", 24900, "subscription"),
    "lead-automation": ("AI & Marketing Automation", 29900, "payment"),
    "branding-design": ("Branding & Design", 19900, "payment"),
    "content-marketing": ("Content & Copywriting", 9900, "payment"),
    "email-sms": ("Email & SMS Marketing", 14900, "subscription"),
    "reputation-management": ("Reputation Management", 9900, "subscription"),
    "ecommerce": ("E-Commerce Solutions", 99900, "payment"),
    "analytics-conversion": ("Analytics & Conversion", 29900, "payment"),
    "business-technology": ("Business Technology", 24900, "payment"),
    "it-support": ("Remote IT Support (1 hour)", 9500, "payment"),
}

def configured():
    return bool(os.getenv("STRIPE_SECRET_KEY") and os.getenv("STRIPE_WEBHOOK_SECRET"))

def database():
    DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB), timeout=15)
    conn.execute("""CREATE TABLE IF NOT EXISTS checkout_orders (
        session_id TEXT PRIMARY KEY, service_slug TEXT NOT NULL,
        customer_email TEXT, amount_total INTEGER, currency TEXT,
        payment_status TEXT NOT NULL, updated_at TEXT NOT NULL
    )""")
    conn.commit()
    return conn

@router.post("/checkout/{slug}")
def checkout(slug: str):
    if slug not in CATALOG:
        raise HTTPException(404, "Unknown service")
    if not configured():
        raise HTTPException(503, "Online checkout is being configured. Please request a consultation.")
    name, cents, mode = CATALOG[slug]
    stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
    origin = "https://rebootsyndicate.com"
    recurring = {"interval": "month"} if mode == "subscription" else None
    price_data = {"currency": "usd", "unit_amount": cents, "product_data": {
        "name": name + (" — monthly starter plan" if recurring else " — starter service"),
        "description": "Scope and deliverables must be agreed in writing before work begins."
    }}
    if recurring:
        price_data["recurring"] = recurring
    try:
        session = stripe.checkout.Session.create(
            mode=mode, line_items=[{"price_data": price_data, "quantity": 1}],
            success_url=origin + "/checkout/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=origin + "/marketing/" + slug,
            client_reference_id=slug,
            billing_address_collection="auto",
            metadata={"service_slug": slug},
        )
    except stripe.StripeError:
        raise HTTPException(502, "Payment provider unavailable. Please try again later.")
    return RedirectResponse(session.url, status_code=303)

@router.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not secret:
        raise HTTPException(503, "Webhook not configured")
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, signature, secret)
    except (ValueError, stripe.SignatureVerificationError):
        raise HTTPException(400, "Invalid webhook signature")
    if event["type"] in {"checkout.session.completed", "checkout.session.async_payment_succeeded",
                         "checkout.session.async_payment_failed"}:
        session = event["data"]["object"]
        slug = session.get("metadata", {}).get("service_slug") or session.get("client_reference_id")
        if slug in CATALOG:
            status = session.get("payment_status", "unpaid")
            if event["type"] == "checkout.session.async_payment_failed":
                status = "failed"
            with database() as conn:
                conn.execute("""INSERT INTO checkout_orders
                    (session_id, service_slug, customer_email, amount_total, currency, payment_status, updated_at)
                    VALUES (?,?,?,?,?,?,?)
                    ON CONFLICT(session_id) DO UPDATE SET
                    customer_email=excluded.customer_email, amount_total=excluded.amount_total,
                    currency=excluded.currency, payment_status=excluded.payment_status,
                    updated_at=excluded.updated_at""", (
                    session["id"], slug, (session.get("customer_details") or {}).get("email"),
                    session.get("amount_total"), session.get("currency"), status,
                    datetime.now(timezone.utc).isoformat()))
    return {"received": True}

@router.get("/checkout/success", response_class=HTMLResponse)
def checkout_success():
    # A redirect is not proof of payment. Only verified webhook events update orders.
    return HTMLResponse("""<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Checkout received | Reboot Syndicate</title>
    <body style="background:#131a1d;color:#fff;font:18px system-ui;padding:10vw;max-width:680px">
    <h1 style="color:#ff6338">THANK YOU.</h1><p>Your checkout has been submitted.
    Payment confirmation is processed separately. We'll contact you to confirm the scope and next steps.</p>
    <a style="color:#ff6338" href="/">RETURN TO REBOOT SYNDICATE</a></body></html>""")
