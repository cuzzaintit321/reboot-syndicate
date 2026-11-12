#!/usr/bin/env python3
"""Restore ONE edge-to-edge image per service detail-page hero.

Run from ~/reboot-syndicate after fetching origin/main.
Only app/static/site.css and the detail-page stylesheet URL are edited.
All original images, homepage tiles, prices, form, database, and local
customizations are retained. Existing CSS/HTML are backed up first.
"""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path.cwd()
CSS_PATH = ROOT / "app/static/site.css"
PAGE_PATH = ROOT / "app/templates/marketing_detail.html"
START = "/* R/S full-frame service-detail artwork: no more cropped dashboards */"
END = "/* End R/S full-frame service-detail artwork */"

if not (ROOT / "docker-compose.yml").is_file() or not CSS_PATH.is_file() or not PAGE_PATH.is_file():
    sys.exit("ERROR: Run this from ~/reboot-syndicate on yeet.")

result = subprocess.run(
    ["git", "show", "origin/main:app/static/site.css"],
    cwd=ROOT, capture_output=True, text=True,
)
if result.returncode:
    sys.exit("ERROR: Can't retrieve the updated CSS from GitHub. Run git fetch origin main.")

upstream = result.stdout
if upstream.count(START) != 1 or upstream.count(END) != 1:
    sys.exit("ERROR: Expected CSS patch is missing or duplicated in GitHub. No changes made.")
patch = upstream[upstream.index(START):upstream.index(END)+len(END)]
if (patch.count("var(--detail-photo)") != 1
        or "background-size:cover,cover;" not in patch
        or "content:none!important;" not in patch):
    sys.exit("ERROR: CSS must fill the hero with one image and disable its duplicate. No changes made.")

before_css = CSS_PATH.read_text(encoding="utf-8")
before_page = PAGE_PATH.read_text(encoding="utf-8")
if START in before_css or END in before_css:
    if before_css.count(START) != 1 or before_css.count(END) != 1:
        sys.exit("ERROR: Existing image-fit CSS block is incomplete. No changes made.")
    a = before_css.index(START)
    b = before_css.index(END,a) + len(END)
    after_css = before_css[:a] + patch + before_css[b:]
else:
    after_css = before_css.rstrip() + "\n\n" + patch + "\n"

# Bypass stale stylesheets without changing the image files or references.
version = sha256(after_css.encode("utf-8")).hexdigest()[:12]
after_page, replacements = re.subn(
    r'href="/static/site\.css(?:\?[^"]*)?"',
    'href="/static/site.css?v=full-detail-' + version + '"',
    before_page, count=1,
)
if replacements != 1:
    sys.exit("ERROR: Can't find the detail-page CSS link. No changes made.")
if 'class="agency-detail-visual"' not in after_page:
    sys.exit("ERROR: Expected service-page illustration missing. No changes made.")

if after_css != before_css or after_page != before_page:
    backup_dir = ROOT / "backups" / (
        "service-image-fit-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    )
    for file in (CSS_PATH, PAGE_PATH):
        target = backup_dir / file.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, target)
    CSS_PATH.write_text(after_css, encoding="utf-8")
    PAGE_PATH.write_text(after_page, encoding="utf-8")
    print("Backups:",backup_dir)
else:
    print("Image-fit CSS already installed and current.")

print("Set one full-bleed image on all 14 service detail-page heroes.")
print("Homepage hover images and the original WebPs/PNGs remain unchanged.")
print("Rebuilding only Reboot Syndicate website...")
subprocess.run(["docker","compose","up","-d","--build","website"],check=True)

# Check installed files inside Docker directly, not the HTTP service while booting.
check = r"""
from pathlib import Path
css = Path('/srv/app/static/site.css').read_text(encoding='utf-8')
page = Path('/srv/app/templates/marketing_detail.html').read_text(encoding='utf-8')
start = '/* R/S full-frame service-detail artwork: no more cropped dashboards */'
end = '/* End R/S full-frame service-detail artwork */'
assert css.count(start) == css.count(end) == 1
block = css[css.index(start):css.index(end)]
assert block.count('var(--detail-photo)') == 1
assert 'background-size:cover,cover;' in block
assert 'content:none!important;' in block
assert 'display:none!important;' in block
assert 'background-repeat:no-repeat' in block
assert 'background-position:center center' in block
assert 'z-index:2' in block
assert 'site.css?v=full-detail-' in page
assert 'class="agency-detail-visual"' in page
print('PASS: One full-bleed image per service page; no duplicates or empty bands.')
"""
result = subprocess.run(
    ["docker","compose","exec","-T","website","python","-c",check],
    text=True,capture_output=True,
)
if result.returncode != 0:
    sys.exit("ERROR: Container verification failed:\n"+result.stdout+result.stderr)
print(result.stdout.strip())
print("Open https://rebootsyndicate.com/marketing/analytics-conversion and press Ctrl+Shift+R.")
