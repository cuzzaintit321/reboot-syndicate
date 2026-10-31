#!/usr/bin/env python3
"""Make Reboot Syndicate's logo consistent and show only starting prices.

Run from ~/reboot-syndicate:
    git fetch origin main
    git show origin/main:scripts/sync_logo_and_starting_prices.py > /tmp/sync_logo_and_starting_prices.py
    python3 /tmp/sync_logo_and_starting_prices.py
    docker compose up -d --build website

This intentionally does NOT git pull or modify Docker Compose, secret files,
customer database records, or other self-hosted websites. Edited files are
backed up before replacement. Can be run more than once.
"""
from datetime import datetime
from pathlib import Path
import re
import shutil

ROOT = Path.cwd()
LOGO_FILE = ROOT / "app/static/images/reboot-logo.png"
if not (ROOT / "docker-compose.yml").is_file():
    raise SystemExit("ERROR: Run this from ~/reboot-syndicate.")
if not LOGO_FILE.is_file():
    raise SystemExit("ERROR: The new logo is missing at app/static/images/reboot-logo.png.")

HEADER_FILES = (
    "app/templates/index.html",
    "app/templates/marketing_detail.html",
    "app/templates/marketing.html",
    "app/templates/thanks.html",
    "app/templates/admin.html",
)
PRICE_FILE = "app/templates/marketing_detail.html"
CSS_FILE = "app/static/site.css"
HEADER_PATTERN = re.compile(r'<a class="wordmark" href="/"[^>]*>[\s\S]*?</a>')
LOGO_ANCHOR = (
    '<a class="wordmark" href="/" aria-label="Reboot Syndicate home">'
    '<img class="rs-brand-logo-image" src="/static/images/reboot-logo.png" '
    'alt="Reboot Syndicate"></a>'
)
PRICE_OPEN = '    <div class="agency-detail-price">'
PRICE_END = '    <div class="agency-detail-actions">'
PRICE_BLOCK = """    <div class="agency-detail-price">
      <span class="agency-detail-price-label">STARTING AT</span>
      <strong>{{ pricing.starting }}</strong>
      <span class="agency-detail-price-unit">{{ pricing.unit }}</span>
    </div>
"""
CSS_MARKER = "/* Unified R/S logo and concise starting-price panel */"
CSS_APPEND = """
/* Unified R/S logo and concise starting-price panel */
.site-header .rs-brand-logo-image{
  display:block;width:250px;max-width:100%;height:auto;object-fit:contain;
}
.agency-detail-price{
  display:flex;flex-wrap:wrap;align-items:baseline;
  gap:5px 9px;width:fit-content;max-width:100%;
  margin:26px 0 30px;padding:22px 26px;
  border:1px solid #506165;background:#10191bd9;
}
.agency-detail-price>.agency-detail-price-label{
  display:block;flex-basis:100%;margin-bottom:4px;
  font:700 11px 'DM Mono',monospace;letter-spacing:.09em;color:#c8d5ce;
}
.agency-detail-price>strong{
  font:900 clamp(47px,5vw,73px)/1 'Barlow Condensed',Impact,sans-serif;
  color:var(--accent);
}
.agency-detail-price>.agency-detail-price-unit{
  font:600 13px 'DM Mono',monospace;color:#d1ded5;
}
@media(max-width:520px){
  .site-header .rs-brand-logo-image{width:205px}
  .agency-detail-price{padding:18px 20px}
}
"""

# Validate and build all changes in memory before writing anything.
edited = {}
for rel in HEADER_FILES:
    path = ROOT / rel
    if not path.exists():
        if rel == PRICE_FILE or rel == HEADER_FILES[0]:
            raise SystemExit("ERROR: Required page missing: " + rel)
        print("Skipping optional page:", rel)
        continue
    original = path.read_text(encoding="utf-8")
    match = HEADER_PATTERN.search(original)
    if not match:
        raise SystemExit("ERROR: Can't safely identify the logo in " + rel)
    updated = original
    if 'src="/static/images/reboot-logo.png"' not in match.group(0):
        updated = original[:match.start()] + LOGO_ANCHOR + original[match.end():]

    if rel == PRICE_FILE:
        start = updated.find(PRICE_OPEN)
        end = updated.find(PRICE_END, start if start >= 0 else 0)
        if start < 0 or end < 0:
            raise SystemExit("ERROR: Expected service price section not found. No changes made.")
        updated = updated[:start] + PRICE_BLOCK + updated[end:]
        if any(term in updated for term in (
                "LOW-END PRICE RANGE / REFERENCE",
                "Illustrative range, not a binding quote.",
                "Starting prices cover a defined basic scope.")):
            raise SystemExit("ERROR: Old price text remains. No changes made.")
    edited[rel] = (original, updated)

css_path = ROOT / CSS_FILE
if not css_path.exists():
    raise SystemExit("ERROR: CSS missing. No changes made.")
css_original = css_path.read_text(encoding="utf-8")
css_updated = css_original
if CSS_MARKER not in css_updated:
    css_updated = css_updated.rstrip() + "\n\n" + CSS_APPEND
edited[CSS_FILE] = (css_original, css_updated)

stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backup_root = ROOT / "backups" / ("logo-starting-price-" + stamp)
changes = 0
for rel, (before, after) in edited.items():
    if before == after:
        print("Already current:", rel)
        continue
    dest = backup_root / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    path = ROOT / rel
    shutil.copy2(path, dest)
    path.write_text(after, encoding="utf-8")
    print("Updated:", rel)
    changes += 1

print("\nLogo image:", LOGO_FILE)
print("Price display: STARTING AT + starting amount + unit only")
print("Changed files:", changes)
if changes:
    print("Original file backups:", backup_root)
print("NEXT: docker compose up -d --build website")
