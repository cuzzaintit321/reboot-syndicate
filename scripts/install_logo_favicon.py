#!/usr/bin/env python3
"""Install the logo-matched all-orange Reboot Syndicate favicon on yeet.

Run from ~/reboot-syndicate after:
    git fetch origin main
    git show origin/main:scripts/install_logo_favicon.py > /tmp/install_logo_favicon.py
    python3 /tmp/install_logo_favicon.py

Safe local patch: fetches only the favicon SVG from the repo, removes stale
favicon <link> tags from local heads and adds a versioned SVG icon. Preserves
other HTML, images, SEO, contact forms, pricing, database and Docker settings.
"""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path.cwd()
ICON = ROOT / "app/static/favicon.svg"
PAGE_PATHS = [
    "app/templates/index.html",
    "app/templates/marketing.html",
    "app/templates/marketing_detail.html",
    "app/templates/brevard_county.html",
    "app/templates/service.html",
    "app/templates/thanks.html",
    "app/templates/admin.html",
]
if not (ROOT / "docker-compose.yml").is_file() or not (ROOT / "app/templates/index.html").is_file():
    sys.exit("ERROR: Run this inside ~/reboot-syndicate on yeet.")

fetch = subprocess.run(
    ["git", "show", "origin/main:app/static/favicon.svg"],
    cwd=ROOT, capture_output=True, text=True
)
if fetch.returncode:
    sys.exit("ERROR: GitHub favicon not available; run git fetch origin main.")

svg = fetch.stdout
try:
    root = ET.fromstring(svg)
except ET.ParseError:
    sys.exit("ERROR: GitHub favicon SVG is invalid. No files changed.")
if not root.tag.endswith("svg") or "#fc4c08" not in svg.lower():
    sys.exit("ERROR: Expected orange brand icon was not found. No files changed.")

version = sha256(svg.encode("utf-8")).hexdigest()[:12]
tag = f'<link rel="icon" type="image/svg+xml" href="/static/favicon.svg?v={version}">'
# All variants, including old PNG, shortcut icon, and outdated touch icons.
icon_links = re.compile(
    r'<link\b(?=[^>]*\brel\s*=\s*["\'](?:icon|shortcut icon|apple-touch-icon)["\'])[^>]*>\s*',
    re.I
)
changes = {ICON: svg.encode("utf-8")}
checked = 0
for relative in PAGE_PATHS:
    path = ROOT / relative
    if not path.is_file():
        continue
    text = path.read_text(encoding="utf-8")
    head = re.search(r"<head(?:\s[^>]*)?>.*?</head>", text, re.I | re.S)
    if not head:
        sys.exit("ERROR: Missing <head> in " + relative + ". No files changed.")
    old_head = head.group(0)
    new_head, _ = icon_links.subn("", old_head)
    if new_head.lower().count("</head>") != 1:
        sys.exit("ERROR: Invalid <head> in " + relative + ". No files changed.")
    new_head = re.sub(r"</head>", "\n" + tag + "\n</head>", new_head, count=1, flags=re.I)
    changes[path] = text[:head.start()].encode() + new_head.encode() + text[head.end():].encode()
    checked += 1

if not checked:
    sys.exit("ERROR: No website templates found. No files changed.")

backup_dir = ROOT / "backups" / (
    "logo-favicon-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f")
)
changed = 0
for path, content in changes.items():
    original = path.read_bytes() if path.is_file() else None
    if original == content:
        print("Already current:", path.relative_to(ROOT))
        continue
    if original is not None:
        backup = backup_dir / path.relative_to(ROOT)
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    changed += 1
    print("Updated:", path.relative_to(ROOT))

print("Files changed:",changed)
print("Backups:", backup_dir if backup_dir.is_dir() else "not needed")
print("Rebuilding only the website service...")
subprocess.run(["docker","compose","up","-d","--build","website"],check=True)

# Verify files directly in the rebuilt container; avoid HTTP timing races.
verify = r"""
from pathlib import Path
import xml.etree.ElementTree as ET
icon=Path('/srv/app/static/favicon.svg')
assert icon.is_file(), 'Favicon not included in Docker'
svg=icon.read_text()
ET.fromstring(svg)
assert '#fc4c08' in svg.lower(), 'Wrong favicon color'
for name in ('index.html','marketing.html','marketing_detail.html',
             'brevard_county.html','service.html','thanks.html','admin.html'):
    path=Path('/srv/app/templates') / name
    if not path.is_file():
        continue
    text=path.read_text()
    assert text.count('rel="icon" type="image/svg+xml"')==1, 'Missing icon in '+name
    assert '/static/favicon.svg?v=' in text, 'Favicon URL not found in '+name
print('PASS: Orange Reboot Syndicate favicon installed on all available site pages.')
"""
check = subprocess.run(
    ["docker","compose","exec","-T","website","python","-c",verify],
    capture_output=True,text=True
)
if check.returncode:
    sys.exit("ERROR: Docker verification failed:\n" + check.stdout + check.stderr)
print(check.stdout.strip())
print("Verify in browser: https://rebootsyndicate.com/static/favicon.svg")
print("Then hard refresh your homepage (Ctrl+Shift+R).")
