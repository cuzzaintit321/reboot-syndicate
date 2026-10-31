#!/usr/bin/env python3
"""Switch the right-hand homepage hero photo between hover-only and always-on.

Usage from ~/reboot-syndicate on yeet:
    python3 scripts/toggle_hero_photo.py hide
    python3 scripts/toggle_hero_photo.py show
    python3 scripts/toggle_hero_photo.py status

This is reversible; it doesn't replace images, touch pricing, or alter the
customer database. It preserves the R/S status bar and 3 process labels.
"""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import argparse
import re
import shutil
import subprocess
import sys

ROOT = Path.cwd()
CSS = ROOT / "app/static/site.css"
HTML = ROOT / "app/templates/index.html"
BEGIN = "/* R/S HERO VISIBILITY TOGGLE BEGIN */"
END = "/* R/S HERO VISIBILITY TOGGLE END */"
PANEL = ".agency-home .agency-hero-photo"

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("mode", choices=("hide", "show", "status"),
                    help="'hide' until hover, 'show' always, or 'status'")
args = parser.parse_args()

if not (ROOT / "docker-compose.yml").is_file() or not CSS.is_file() or not HTML.is_file():
    sys.exit("ERROR: Run this from ~/reboot-syndicate on yeet.")

css_before = CSS.read_text(encoding="utf-8")
html_before = HTML.read_text(encoding="utf-8")
if not all(s in html_before for s in ("agency-hero-photo-img", "agency-visual-header", "agency-dashboard")):
    sys.exit("ERROR: Expected homepage hero markup missing; no changes made.")

block_pattern = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.S)
blocks = list(block_pattern.finditer(css_before))
if len(blocks) > 1 or (BEGIN in css_before and not blocks):
    sys.exit("ERROR: Existing hero toggle markers are incomplete or duplicated; no changes made.")

if args.mode == "status":
    if not blocks:
        print("Hero toggle: not installed (site's existing CSS decides visibility).")
    else:
        current = blocks[0].group()
        print("Hero toggle:", "hover-only" if "/* mode: hide */" in current else
              "always visible" if "/* mode: show */" in current else "unknown")
    sys.exit(0)

opacity = "0" if args.mode == "hide" else "1"
hover_rules = (
    f"""{PANEL}:hover > .agency-hero-photo-img,
{PANEL}:focus-within > .agency-hero-photo-img{{
  opacity:1!important;
}}
""" if args.mode == "hide" else ""
)
block = f"""{BEGIN}
/* mode: {args.mode} */
/* Only the photograph changes; the status/process labels stay visible. */
{PANEL}{{
  background:#111a1d!important;
}}
{PANEL} > .agency-hero-photo-img{{
  opacity:{opacity}!important;
  transition:opacity .35s ease!important;
}}
{hover_rules}@media (prefers-reduced-motion:reduce){{
  {PANEL} > .agency-hero-photo-img{{
    transition:none!important;
  }}
}}
{END}"""

if blocks:
    css_after = css_before[:blocks[0].start()] + css_before[blocks[0].end():]
else:
    css_after = css_before

# Always place the switch LAST, after any earlier image rules.
css_after = css_after.rstrip() + "\n\n" + block + "\n"

# Make browsers fetch the updated CSS instead of an older cached stylesheet.
digest = sha256(css_after.encode("utf-8")).hexdigest()[:12]
new_href = f'href="/static/site.css?v=hero-{args.mode}-{digest}"'
html_after, substitutions = re.subn(
    r'href="/static/site\.css(?:\?[^"]*)?"', new_href, html_before, count=1
)
if substitutions != 1:
    sys.exit("ERROR: Homepage stylesheet link not found; no changes made.")

if css_after != css_before or html_after != html_before:
    backup_dir = ROOT / "backups" / (
        "hero-photo-toggle-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    )
    for source in (CSS, HTML):
        backup = backup_dir / source.relative_to(ROOT)
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, backup)
    if css_after != css_before:
        CSS.write_text(css_after, encoding="utf-8")
    if html_after != html_before:
        HTML.write_text(html_after, encoding="utf-8")
    print("Backup:", backup_dir)
else:
    print("No file changes needed.")

print("Homepage hero photo:", "hidden until hover" if args.mode == "hide" else "always visible")
print("Status and process labels: unchanged")
print("Rebuilding only the website container...")
subprocess.run(["docker", "compose", "up", "-d", "--build", "website"], check=True)

# Verify files inside the rebuilt container directly, without a startup-timing HTTP request.
verify_source = r"""
from pathlib import Path
import re
css = Path('/srv/app/static/site.css').read_text(encoding='utf-8')
html = Path('/srv/app/templates/index.html').read_text(encoding='utf-8')
begin = '/* R/S HERO VISIBILITY TOGGLE BEGIN */'
end = '/* R/S HERO VISIBILITY TOGGLE END */'
assert begin in css and end in css
rule = css[css.rfind(begin):css.rfind(end)]
assert '/* mode: MODE */' in rule
assert 'opacity:OPACITY!important;' in rule
assert 'site.css?v=hero-MODE-' in html
assert 'agency-visual-header' in html and 'agency-dashboard' in html
print('PASS: Homepage hero photo set to MODE in rebuilt Docker container.')
""".replace("MODE", args.mode).replace("OPACITY", opacity)
result = subprocess.run(
    ["docker", "compose", "exec", "-T", "website", "python", "-c", verify_source],
    text=True, capture_output=True
)
if result.returncode:
    sys.exit("ERROR: Container file verification failed:\n" + result.stdout + result.stderr)
print(result.stdout.strip())
print("Refresh https://rebootsyndicate.com with Ctrl+Shift+R.")
