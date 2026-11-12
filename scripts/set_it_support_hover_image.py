#!/usr/bin/env python3
"""Use the new System Diagnostics PNG as the IT Support homepage hover photo.

Run on yeet from ~/reboot-syndicate. This script changes only local
app/static/site.css and the homepage stylesheet URL; it does not change
any service detail pages, photos, Docker configuration, environment,
customers, or other services. Backs up files before edits.
"""
from pathlib import Path
from datetime import datetime
from hashlib import sha256
import re
import shutil
import subprocess
import sys

root = Path.cwd()
logo_file = root / "app/static/images/it-support-detail.png"
css_path = root / "app/static/site.css"
html_path = root / "app/templates/index.html"
if not (root / "docker-compose.yml").is_file() or not css_path.is_file() or not html_path.is_file():
    sys.exit("ERROR: Run from ~/reboot-syndicate on yeet.")
if not logo_file.is_file():
    sys.exit(
        "ERROR: New diagnostics image missing at app/static/images/it-support-detail.png.\n"
        'On Fedora, run:\nscp ~/Downloads/"Neon System Diagnostics Workstation.png" '
        "yeet:~/reboot-syndicate/app/static/images/it-support-detail.png"
    )
image_bytes = logo_file.read_bytes()
if not image_bytes.startswith(bytes.fromhex("89504e470d0a1a0a")):
    sys.exit("ERROR: The diagnostics image is not a PNG. No files changed.")

digest = sha256(image_bytes).hexdigest()[:12]
marker = "/* R/S IT Support tile: diagnostics workstation hover image */"
endmarker = "/* End R/S IT Support diagnostics tile */"
overrides = """
""" + marker + """
.agency-home .agency-service-card[href="/marketing/it-support"]{
  --card-photo:url("/static/images/it-support-detail.png?v=""" + digest + """")!important;
}
.agency-home .agency-service-card[href="/marketing/it-support"]::before{
  background-size:cover,cover!important;
  background-position:center,center!important;
}
/* End R/S IT Support diagnostics tile */
"""

css_before = css_path.read_text(encoding="utf-8")
# Replace the GitHub placeholder or any prior run's matching block, keeping
# everything else exactly as found locally.
css_after = css_before
if marker in css_after:
    start = css_after.find(marker)
    end = css_after.find(endmarker, start)
    if end < 0:
        sys.exit("ERROR: Existing diagnostics CSS marker is incomplete. No files changed.")
    css_after = css_after[:start] + css_after[end + len(endmarker):]
css_after = css_after.rstrip() + "\n" + overrides.strip() + "\n"

# Older installers set --card-photo with !important, so ensure new rule
# appears LAST; unchanged hover-only opacity rules still apply to every tile.
html_before = html_path.read_text(encoding="utf-8")
style_key = sha256(css_after.encode("utf-8")).hexdigest()[:12]
html_after, matched = re.subn(
    r'href="/static/site\.css(?:\?[^"]*)?"',
    'href="/static/site.css?v=it-hover-' + style_key + '"',
    html_before,
    count=1
)
if matched != 1:
    sys.exit("ERROR: Cannot find homepage site.css link. No files changed.")

if css_before != css_after or html_before != html_after:
    backup = root / "backups" / (
        "it-support-hover-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    )
    for file in (css_path, html_path):
        dest = backup / file.relative_to(root)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, dest)
    if css_before != css_after:
        css_path.write_text(css_after, encoding="utf-8")
    if html_before != html_after:
        html_path.write_text(html_after, encoding="utf-8")
    print("Backups:", backup)
else:
    print("CSS and homepage already set to new diagnostics hover image.")

print("Image SHA256:", digest)
print("Rebuilding only the website...")
subprocess.run(["docker", "compose", "up", "-d", "--build", "website"], check=True)

# Confirm that Docker actually has the PNG, CSS points to its version,
# and the website serves the image. Then check the hover-only rules.
verify_source = """
from pathlib import Path
from hashlib import sha256
from urllib.request import urlopen

image = Path('/srv/app/static/images/it-support-detail.png')
css = Path('/srv/app/static/site.css').read_text(encoding='utf-8')
home = Path('/srv/app/templates/index.html').read_text(encoding='utf-8')
digest = sha256(image.read_bytes()).hexdigest()[:12]
assert 'it-support-detail.png?v=' + digest in css, 'CSS not updated to actual PNG'
assert 'R/S service image hover-only visibility' in css, 'Hover-only visibility rule missing'
assert 'opacity:0!important' in css, 'Hover-off visibility rule missing'
assert 'opacity:1!important' in css, 'Hover-on visibility rule missing'
assert 'it-hover-' in home, 'Homepage stylesheet cache bust missing'
with urlopen('http://127.0.0.1:8000/static/images/it-support-detail.png?v='+digest, timeout=12) as res:
    assert res.status == 200, 'Image is not served'
    assert res.read(8) == bytes.fromhex('89504e470d0a1a0a'), 'Wrong image bytes'
print('PASS: New diagnostics photo is served and IT tile shows it on hover only.')
"""
result = subprocess.run(
    ["docker", "compose", "exec", "-T", "website", "python", "-c", verify_source],
    capture_output=True, text=True
)
if result.returncode:
    sys.exit("ERROR: Verification failed:\n" + result.stdout + result.stderr)
print(result.stdout.strip())
print("Reload https://rebootsyndicate.com with Ctrl+Shift+R.")
