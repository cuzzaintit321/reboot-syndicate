from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
from html import escape

router = APIRouter()

SERVICES = {
    "website-design": (
        "Website Design",
        "WEBSITES BUILT TO WORK.",
        "Responsive websites, landing pages, redesigns, contact forms, and practical business websites."
    ),
    "local-seo": (
        "Local SEO",
        "GET FOUND LOCALLY.",
        "Local keyword research, on-page optimization, technical SEO checks, and search-friendly content."
    ),
    "google-business-profile": (
        "Google Business Profile",
        "PUT YOUR BUSINESS ON THE MAP.",
        "Google Business Profile setup guidance, listing improvements, photos, business details, and ongoing optimization."
    ),
    "social-media": (
        "Social Media Content",
        "CONTENT THAT CONNECTS.",
        "Branded social media graphics, content planning, Facebook and Instagram posts, and publishing assistance."
    ),
    "digital-advertising": (
        "Digital Advertising",
        "REACH THE RIGHT AUDIENCE.",
        "Google Ads and Meta Ads campaign planning, setup, targeting, and performance monitoring."
    ),
    "lead-automation": (
        "Lead Automation",
        "TURN INQUIRIES INTO OPPORTUNITIES.",
        "Lead capture forms, inquiry organization, response drafts, and approval-based follow-up workflows."
    ),
    "branding-design": (
        "Branding & Graphic Design",
        "MAKE YOUR BRAND RECOGNIZABLE.",
        "Logo concepts, brand kits, business cards, social templates and campaign graphics."
    ),
    "content-marketing": (
        "Content Marketing & Copywriting",
        "MAKE EVERY WORD COUNT.",
        "Website copy, blog content, newsletters, content calendars and search-oriented writing."
    ),
    "email-sms": (
        "Email & SMS Marketing",
        "STAY IN TOUCH. STAY TOP OF MIND.",
        "Permission-based email and SMS campaigns, segmentation, customer follow-ups and unsubscribe workflows."
    ),
    "reputation-management": (
        "Reputation Management",
        "BUILD TRUST THAT LASTS.",
        "Legitimate review request workflows, review monitoring, customer feedback and response support."
    ),
    "ecommerce": (
        "E-commerce Solutions",
        "TAKE YOUR STORE ONLINE.",
        "Online shops, product catalogs, payment integrations, storefront updates and optimization."
    ),
    "analytics-conversion": (
        "Analytics & Conversion Optimization",
        "KNOW WHAT WORKS.",
        "Analytics dashboards, conversion tracking, reporting and landing-page improvements."
    ),
    "business-technology": (
        "Business Technology Services",
        "BUILD ON SOLID TECH.",
        "Domains, DNS, SSL, business email, hosting, security and software integrations."
    ),
    "it-support": (
        "Computer Repair & IT Support",
        "WE STILL FIX THE TECH.",
        "Local computer repair, Wi-Fi and networking, device setup, backups and small-business IT."
    ),
}

@router.get("/marketing/{slug}", response_class=HTMLResponse)
def marketing_service(slug: str):
    if slug not in SERVICES:
        raise HTTPException(status_code=404)

    name, headline, description = SERVICES[slug]

    return HTMLResponse(f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(name)} | Reboot Syndicate</title>
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:#0b0e10;color:#f4f1e8;font-family:Arial,sans-serif}}
header{{padding:25px 7%;border-bottom:1px solid #343b3e}}
header a{{color:#ff5c2a;text-decoration:none;font-weight:800}}
main{{max-width:1150px;margin:auto;padding:95px 7%;min-height:75vh}}
.eyebrow{{font-size:12px;letter-spacing:3px;color:#ff5c2a;font-weight:bold}}
h1{{font-size:clamp(48px,8vw,100px);line-height:1;margin:30px 0;text-transform:uppercase}}
.description{{font-size:21px;line-height:1.8;color:#b5bdb8;max-width:800px}}
.button{{display:inline-block;margin-top:40px;padding:22px 30px;background:#ff5c2a;color:#111;text-decoration:none;font-weight:800}}
.button:hover{{background:#ff875e}}
footer{{padding:30px 7%;border-top:1px solid #343b3e;color:#9ba6a1}}
</style>
</head>
<body>
<header><a href="/">R/S REBOOT SYNDICATE</a></header>
<main>
<p class="eyebrow">DIGITAL MARKETING / {escape(name.upper())}</p>
<h1>{escape(headline)}</h1>
<p class="description">{escape(description)}</p>
<a class="button" href="/#request">REQUEST THIS SERVICE ↗</a>
</main>
<footer>© 2026 Reboot Syndicate</footer>
</body>
</html>
""")
