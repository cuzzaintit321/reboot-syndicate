#!/usr/bin/env python3
"""Apply Reboot Syndicate's 14 service prices to a locally customized checkout.

Safely transplants only pricing markup, pricing data, and related styles from
origin/main. Keeps local logo, contact details, hero images and Docker Compose
configuration unchanged. Does not touch customer records or Docker volumes.

On yeet:
  cd ~/reboot-syndicate
  git fetch origin main
  git show origin/main:scripts/install_service_prices.py > /tmp/install_service_prices.py
  python3 /tmp/install_service_prices.py
  docker compose up -d --build website
"""
from pathlib import Path
from datetime import datetime
import ast
import re
import shutil
import subprocess

ROOT = Path.cwd()
PATHS = (
    "app/templates/index.html",
    "app/marketing_services.py",
    "app/templates/marketing_detail.html",
    "app/static/site.css",
)
SLUGS = (
    "website-design", "local-seo", "google-business-profile", "social-media",
    "digital-advertising", "lead-automation", "branding-design", "content-marketing",
    "email-sms", "reputation-management", "ecommerce", "analytics-conversion",
    "business-technology", "it-support",
)
PRICE_MARKER = "# User-selected entry-level pricing."
CSS_MARKER = "/* Reboot Syndicate service-specific starting prices:"

if not (ROOT / "docker-compose.yml").is_file():
    raise SystemExit("Run this script from ~/reboot-syndicate.")

def git_source(path):
    result = subprocess.run(
        ["git", "show", "origin/main:" + path],
        cwd=ROOT, capture_output=True, text=True, check=False
    )
    if result.returncode:
        raise SystemExit("Cannot read GitHub version of " + path
                         + ". Run: git fetch origin main")
    return result.stdout

upstream = {path: git_source(path) for path in PATHS}
original = {}
for path in PATHS:
    file = ROOT / path
    original[path] = file.read_text(encoding="utf-8") if file.exists() else None

# The homepage may have a custom, locally edited logo or hero. Never replace it.
tile_pattern = (
    r'(<a class="agency-service-card" href="/marketing/{slug}">'
    r'[\s\S]*?)(<span class="agency-arrow">EXPLORE SERVICE ↗</span></a>)'
)
index = original[PATHS[0]]
if index is None:
    raise SystemExit("Homepage template is missing; no changes made.")

for slug in SLUGS:
    pat = re.compile(tile_pattern.format(slug=re.escape(slug)))
    up_match = pat.search(upstream[PATHS[0]])
    local_match = pat.search(index)
    if up_match is None or local_match is None:
        raise SystemExit(f"Cannot locate {slug} service tile in GitHub/local HTML. No changes made.")

    if 'class="agency-card-pricing"' in local_match.group(1):
        continue

    source_inner = up_match.group(1)
    start = source_inner.find('<span class="agency-card-pricing">')
    if start == -1:
        raise SystemExit(f"No pricing block found for {slug} in GitHub.")
    price_markup = source_inner[start:]
    # Preserve each local card intact; insert only the pricing block.
    index = index[:local_match.start(2)] + price_markup + index[local_match.start(2):]

if index.count('class="agency-card-pricing"') != 14:
    raise SystemExit("Expected exactly 14 price labels on homepage. No changes made.")

# Keep existing detailed descriptions. Add/refresh only pricing dictionary and context.
service_source = upstream[PATHS[1]]
service = original[PATHS[1]]
if service is None:
    service = service_source
else:
    if PRICE_MARKER not in service_source:
        raise SystemExit("Pricing source mapping missing in GitHub.")
    begin = service_source.index("# " + PRICE_MARKER.lstrip("# "))
    end = service_source.index("@router.get('/marketing/{slug}')", begin)
    pricing_section = service_source[begin:end].rstrip() + "\n\n"
    if "SERVICE_PRICING =" not in service:
        anchor = "@router.get('/marketing/{slug}')"
        if anchor not in service:
            raise SystemExit("Local service router is different. No changes made.")
        service = service.replace(anchor, pricing_section + anchor, 1)
    old = "{'service':service, 'slug':slug}"
    new = "{'service':service, 'slug':slug, 'pricing':SERVICE_PRICING[slug]}"
    if new not in service:
        if old not in service:
            raise SystemExit("Local service detail route differs. No changes made.")
        service = service.replace(old, new, 1)
ast.parse(service, filename=PATHS[1])

# Service detail content comes from the backend, so one reusable template covers all.
detail_source = upstream[PATHS[2]]
detail = original[PATHS[2]]
if detail is None:
    detail = detail_source
elif 'class="agency-detail-price"' not in detail:
    anchor = '    <div class="agency-detail-actions">'
    begin = detail_source.index('    <div class="agency-detail-price">')
    end = detail_source.index(anchor, begin)
    detail_markup = detail_source[begin:end]
    if anchor not in detail:
        raise SystemExit("Cannot place pricing in local detail template. No changes made.")
    detail = detail.replace(anchor, detail_markup + anchor, 1)

# Append only pricing styles; preserve existing locally customized hero and logo CSS.
css_source = upstream[PATHS[3]]
css = original[PATHS[3]]
if css is None:
    raise SystemExit("Site CSS is missing; no changes made.")
if CSS_MARKER not in css:
    start = css_source.find(CSS_MARKER)
    if start == -1:
        raise SystemExit("Pricing CSS missing from GitHub; no changes made.")
    css = css.rstrip() + "\n\n" + css_source[start:]

proposed = dict(zip(PATHS, (index, service, detail, css)))
stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backup = ROOT / "backups" / ("service-prices-" + stamp)
for path, new in proposed.items():
    before = original[path]
    file = ROOT / path
    if before == new:
        print("Already current:", path)
        continue
    if before is not None:
        destination = backup / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, destination)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(new, encoding="utf-8")
    print("Updated:", path)

print("\nValidated all 14 service prices.")
print("Your local logo, Docker settings, and customer database were not touched.")
if backup.exists():
    print("Backups:", backup)
print("Next: docker compose up -d --build website")
