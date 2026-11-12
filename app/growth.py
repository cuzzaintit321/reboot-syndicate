"""Evidence and pricing pages; reuse the existing service and pricing registry."""
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.marketing_services import SERVICES, SERVICE_PRICING
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/work")
@router.get("/pricing")
def growth_page(request: Request):
    is_work = request.url.path == "/work"
    title = "Selected work by Reboot Syndicate" if is_work else "Reboot Syndicate service pricing"
    schema = {"@context": "https://schema.org", "@type": "CollectionPage", "name": title,
              "url": "https://rebootsyndicate.com" + request.url.path,
              "isPartOf": {"@type": "WebSite", "name": "Reboot Syndicate", "url": "https://rebootsyndicate.com/"}}
    return templates.TemplateResponse(request, "growth_work.html" if is_work else "growth_pricing.html",
                                      {"services": SERVICES, "pricing": SERVICE_PRICING, "page_schema": schema})
