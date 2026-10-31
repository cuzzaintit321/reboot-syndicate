#!/usr/bin/env python3
"""Restore hover-only service images on the locally customized website.

Run from ~/reboot-syndicate. Does not git pull or alter images, forms, prices,
Docker settings or customer records. Backs up CSS and homepage HTML.
"""
from pathlib import Path
from datetime import datetime
from hashlib import sha256
import re
import shutil
import subprocess

root = Path.cwd()
css_file = root / "app/static/site.css"
home_file = root / "app/templates/index.html"
if not (root / "docker-compose.yml").is_file() or not css_file.is_file() or not home_file.is_file():
    raise SystemExit("Run from ~/reboot-syndicate (site files missing).")

marker = "/* R/S service image hover-only visibility (all 14 tiles) */"
override = """
/* R/S service image hover-only visibility (all 14 tiles) */
.agency-home .agency-service-card::before{
  opacity:0!important;
}
.agency-home .agency-service-card:hover::before,
.agency-home .agency-service-card:focus-visible::before{
  opacity:1!important;
}
"""

css_before = css_file.read_text(encoding="utf-8")
html_before = home_file.read_text(encoding="utf-8")
# Append this LAST so the old v3 opacity:.92!important rule can't override it.
if marker in css_before:
    css_after = css_before
    # Existing marked override could be followed by newer CSS; ensure the
    # final intended rule is present at the end if necessary.
    if not css_before.rstrip().endswith(override.strip()):
        css_after = css_before.rstrip() + "\n\n" + override
else:
    css_after = css_before.rstrip() + "\n\n" + override
version = sha256(css_after.encode("utf-8")).hexdigest()[:12]
pattern = r'href="/static/site\.css(?:\?[^"]*)?"'
html_after, n = re.subn(
    pattern, f'href="/static/site.css?v=hover-{version}"',
    html_before, count=1
)
if n != 1:
    raise SystemExit("Can't locate homepage stylesheet link. No files changed.")

if css_before != css_after or html_before != html_after:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = root / "backups" / f"hover-only-{stamp}"
    for src in (css_file, home_file):
        target = backup / src.relative_to(root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
    if css_before != css_after:
        css_file.write_text(css_after, encoding="utf-8")
    if html_before != html_after:
        home_file.write_text(html_after, encoding="utf-8")
    print("Backed up CSS and homepage:", backup)
else:
    print("Hover-only CSS and homepage cache-busting already applied.")

print("Rebuilding only the website container...")
subprocess.run(["docker", "compose", "up", "-d", "--build", "website"], check=True)
verify = subprocess.run(
    ["docker", "compose", "exec", "-T", "website", "python", "-c",
     "from pathlib import Path; s=Path('/srv/app/static/site.css').read_text(); "
     "assert '/* R/S service image hover-only visibility (all 14 tiles) */' in s; "
     "assert s.rfind('opacity:0!important') > s.rfind('opacity:.92!important'); "
     "print('Verified: all service images hidden until hover or keyboard focus')"],
    check=True
)
print("DONE. Refresh https://rebootsyndicate.com with Ctrl+Shift+R.")
