#!/usr/bin/env python3
"""Install the user's new IT Support diagnostics photo without changing tile images.

Run from ~/reboot-syndicate after copying the new PNG into:
    app/static/images/it-support-detail.png

This updates only two local source files; it does not use git pull,
change homepage tiles, Docker configuration, env secrets or databases.
It backs up each modified file and checks the live container after rebuild.
"""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import ast
import re
import shutil
import subprocess
import sys

ROOT = Path.cwd()
IMAGE = ROOT / "app/static/images/it-support-detail.png"
SOURCE = ROOT / "app/marketing_services.py"
TEMPLATE = ROOT / "app/templates/marketing_detail.html"

if not (ROOT / "docker-compose.yml").is_file():
    sys.exit("ERROR: Run this from ~/reboot-syndicate on yeet.")
if not IMAGE.is_file():
    sys.exit(
        "ERROR: New PNG not found at app/static/images/it-support-detail.png\n"
        "From Fedora, run:\n"
        'scp ~/Downloads/"Neon System Diagnostics Workstation.png" '
        "yeet:~/reboot-syndicate/app/static/images/it-support-detail.png"
    )
if not IMAGE.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
    sys.exit("ERROR: New diagnostics file is not a real PNG. No changes made.")
if not SOURCE.is_file() or not TEMPLATE.is_file():
    sys.exit("ERROR: Service source or template missing. No changes made.")

old_assign = (
    "    image_path = Path(__file__).resolve().parent / "
    "'static' / 'images' / f'{slug}.webp'"
)
new_assign = """    image_dir = Path(__file__).resolve().parent / 'static' / 'images'
    detail_override = image_dir / 'it-support-detail.png'
    image_path = (
        detail_override
        if slug == 'it-support' and detail_override.is_file()
        else image_dir / f'{slug}.webp'
    )"""
context_old = "        'image_version': image_version,"
context_new = "        'image_version': image_version,\n        'image_filename': image_path.name,"
old_url = """style="--detail-photo:url('/static/images/{{ slug }}.webp?v={{ image_version }}')""" + '"'
new_url = """style="--detail-photo:url('/static/images/{{ image_filename }}?v={{ image_version }}')""" + '"'

old_source = SOURCE.read_text(encoding="utf-8")
updated_source = old_source
if "detail_override = image_dir / 'it-support-detail.png'" not in updated_source:
    if old_assign not in updated_source:
        sys.exit("ERROR: Local service-image code differs. No files changed.")
    updated_source = updated_source.replace(old_assign, new_assign, 1)
if context_new not in updated_source:
    if context_old not in updated_source:
        sys.exit("ERROR: Local route lacks image_version context. No files changed.")
    updated_source = updated_source.replace(context_old, context_new, 1)
if "from hashlib import sha256" not in updated_source or "from pathlib import Path" not in updated_source:
    sys.exit("ERROR: Required imports are missing. No files changed.")
ast.parse(updated_source, filename=str(SOURCE))

old_template = TEMPLATE.read_text(encoding="utf-8")
# Earlier instructions inserted a Jinja conditional directly into the
# section's opening tag. Replace that entire tag, not just the old URL.
# This handles the unmodified template, the earlier conditional variant,
# and a template already updated to image_filename.
hero_tag = re.compile(r'<section\\s+class="agency-detail-hero"[^>]*>')
matches = list(hero_tag.finditer(old_template))
if len(matches) != 1:
    sys.exit("ERROR: Expected one hero section; found " + str(len(matches))
             + ". No files changed.")
canonical_tag = '<section class="agency-detail-hero" ' + new_url + '>'
updated_template = (
    old_template[:matches[0].start()] + canonical_tag
    + old_template[matches[0].end():]
)

backup_root = ROOT / "backups" / (
    "it-support-diagnostics-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f")
)
for file, previous, updated in (
    (SOURCE, old_source, updated_source),
    (TEMPLATE, old_template, updated_template),
):
    if previous == updated:
        print("Already updated:", file.relative_to(ROOT))
        continue
    target = backup_root / file.relative_to(ROOT)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(file, target)
    file.write_text(updated, encoding="utf-8")
    print("Updated:", file.relative_to(ROOT))

digest = sha256(IMAGE.read_bytes()).hexdigest()[:12]
print("New detail photo:", IMAGE.name)
print("Image cache key:", digest)
print("Homepage hover photo: unchanged")
print("Rebuilding only the Reboot Syndicate website...")
subprocess.run(["docker", "compose", "up", "-d", "--build", "website"], check=True)

# Verify the container really serves the new detail photo, not only its source files.
check = r"""
from urllib.request import urlopen
from hashlib import sha256
from pathlib import Path

img = Path('/srv/app/static/images/it-support-detail.png')
assert img.is_file(), 'PNG missing in container'
digest = sha256(img.read_bytes()).hexdigest()[:12]
with urlopen('http://127.0.0.1:8000/marketing/it-support', timeout=12) as response:
    page = response.read().decode('utf-8')
expected = '/static/images/it-support-detail.png?v=' + digest
assert expected in page, 'IT detail page still references old background photo'
with urlopen('http://127.0.0.1:8000' + expected, timeout=12) as response:
    assert response.read(8) == bytes.fromhex('89504e470d0a1a0a'), 'New photo not served as PNG'
print('PASS: Live IT Support page serves the new diagnostics image: ' + expected)
"""
run = subprocess.run(
    ["docker", "compose", "exec", "-T", "website", "python", "-c", check],
    capture_output=True, text=True
)
if run.returncode != 0:
    sys.exit("ERROR: Website verification failed:\n" + run.stdout + run.stderr)
print(run.stdout.strip())
if backup_root.is_dir():
    print("Backups:", backup_root)
print("DONE. Hard refresh https://rebootsyndicate.com/marketing/it-support")
