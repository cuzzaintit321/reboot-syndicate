#!/usr/bin/env python3
"""Darken only the homepage IT Support hover image, without touching the PNG."""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import re
import shutil
import subprocess
import sys

root = Path.cwd()
css_file = root / "app/static/site.css"
home_file = root / "app/templates/index.html"
if not (root / "docker-compose.yml").is_file() or not css_file.is_file() or not home_file.is_file():
    sys.exit("ERROR: Run from ~/reboot-syndicate on yeet.")

marker = "/* R/S IT Support hover-photo brightness match */"
rule = """/* R/S IT Support hover-photo brightness match */
/* Photo gets 38% darker; text, icons and pricing stay unchanged. */
.agency-home .agency-service-card[href="/marketing/it-support"]::before{
  filter:brightness(.62) saturate(.85) contrast(1.03)!important;
}
"""
css_before = css_file.read_text(encoding="utf-8")
css_after = css_before
if marker in css_after:
    # Replace the previously installed version if present.
    css_after, count = re.subn(
        r'/\* R/S IT Support hover-photo brightness match \*/.*?'
        r'\.agency-home \.agency-service-card\[href="/marketing/it-support"\]::before\s*\{[^}]*\}',
        rule.strip(),
        css_after,
        count=1,
        flags=re.S
    )
    if count != 1:
        sys.exit("ERROR: Existing IT Support brightness rule is malformed. No files changed.")
else:
    css_after = css_after.rstrip() + "\n\n" + rule

home_before = home_file.read_text(encoding="utf-8")
digest = sha256(css_after.encode("utf-8")).hexdigest()[:12]
home_after, n = re.subn(
    r'href="/static/site\.css(?:\?[^"]*)?"',
    'href="/static/site.css?v=it-darker-' + digest + '"',
    home_before,
    count=1
)
if n != 1:
    sys.exit("ERROR: Homepage stylesheet URL not found. No files changed.")

if css_after != css_before or home_after != home_before:
    backup_dir = root / "backups" / (
        "it-hover-brightness-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    )
    for file in (css_file, home_file):
        target = backup_dir / file.relative_to(root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, target)
    if css_before != css_after:
        css_file.write_text(css_after, encoding="utf-8")
    if home_before != home_after:
        home_file.write_text(home_after, encoding="utf-8")
    print("Backups:", backup_dir)
else:
    print("Brightness and cache-busting already current.")

print("IT Support hover brightness: 62% (38% darker)")
print("Other 13 tile images and text: unchanged")
print("Rebuilding only website...")
subprocess.run(["docker", "compose", "up", "-d", "--build", "website"], check=True)

# Verify compiled CSS and homepage, not HTTP availability immediately at startup.
verify_code = """
from pathlib import Path
css=Path('/srv/app/static/site.css').read_text()
html=Path('/srv/app/templates/index.html').read_text()
assert 'filter:brightness(.62) saturate(.85) contrast(1.03)!important;' in css
assert 'opacity:0!important' in css and 'opacity:1!important' in css
assert 'it-darker-' in html
print('PASS: Darkened IT hover photo installed; hover-only opacity rules retained.')
"""
subprocess.run(
    ["docker", "compose", "exec", "-T", "website", "python", "-c", verify_code],
    check=True,
)
print("Refresh https://rebootsyndicate.com with Ctrl+Shift+R.")
