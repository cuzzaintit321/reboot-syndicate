"""Search engine discovery endpoints for Reboot Syndicate.

Public sitemap contains the homepage, marketing overview, and the 14
individual service detail pages. Only canonical URLs are listed.
"""
from xml.etree.ElementTree import Element, SubElement, tostring

from fastapi import APIRouter, Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates

from app.marketing_services import SERVICES

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
BASE_URL = "https://rebootsyndicate.com"


@router.get("/robots.txt", include_in_schema=False)
def robots_txt():
    body = (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {BASE_URL}/sitemap.xml\n"
    )
    return Response(content=body, media_type="text/plain")


@router.get("/sitemap.xml", include_in_schema=False)
def sitemap_xml():
    # Generated from the actual service route registry so new services appear
    # automatically without manually editing XML.
    urls = ["/", "/marketing", "/brevard-county"] + [f"/marketing/{slug}" for slug in SERVICES]
    root = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for path in urls:
        url = SubElement(root, "url")
        SubElement(url, "loc").text = BASE_URL + path
    xml = b'<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(
        root, encoding="utf-8", xml_declaration=False
    )
    return Response(content=xml, media_type="application/xml")


@router.get("/brevard-county", include_in_schema=False)
def brevard_county_services(request: Request):
    """One useful county service landing page; avoid duplicative city doorway pages."""
    return templates.TemplateResponse(request, "brevard_county.html", {})
