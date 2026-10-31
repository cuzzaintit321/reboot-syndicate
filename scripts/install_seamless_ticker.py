#!/usr/bin/env python3
"""Make Reboot Syndicate's orange homepage ticker loop forever without gaps.

Run on yeet, from ~/reboot-syndicate, after fetching origin main:
  git show origin/main:scripts/install_seamless_ticker.py > /tmp/install_seamless_ticker.py
  python3 /tmp/install_seamless_ticker.py

Only the homepage ticker markup, its marked CSS rule, and homepage stylesheet
version are edited. Prices, SEO, favicon, images, contact form and data stay
unchanged. Original files are backed up and only website Docker is rebuilt.
"""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path.cwd()
HOME = ROOT / "app/templates/index.html"
CSS = ROOT / "app/static/site.css"
START = "/* R/S seamless orange services ticker */"
END = "/* End R/S seamless orange services ticker */"
TICKER_PATTERN = re.compile(
    r'<div class="ticker" aria-hidden="true">.*?</div></div>', re.S
)
if not (ROOT / "docker-compose.yml").is_file() or not HOME.is_file() or not CSS.is_file():
    sys.exit("ERROR: Run in ~/reboot-syndicate on yeet.")

def upstream(path):
    result = subprocess.run(
        ["git", "show", "origin/main:" + path], cwd=ROOT,
        capture_output=True, text=True
    )
    if result.returncode:
        sys.exit("ERROR: GitHub source not found for " + path +
                 ". Run git fetch origin main first.")
    return result.stdout

home_before = HOME.read_text(encoding="utf-8")
css_before = CSS.read_text(encoding="utf-8")
home_source = upstream("app/templates/index.html")
css_source = upstream("app/static/site.css")
local_matches = list(TICKER_PATTERN.finditer(home_before))
remote_matches = list(TICKER_PATTERN.finditer(home_source))
if len(local_matches) != 1 or len(remote_matches) != 1:
    sys.exit("ERROR: Couldn't uniquely identify the homepage ticker. No files changed.")

ticker = remote_matches[0].group()
segments = re.findall(
    r'<span class="ticker-segment">(.*?)</span>', ticker, re.S
)
if len(segments) != 2 or segments[0] != segments[1]:
    sys.exit("ERROR: New ticker must have two identical segments. No files changed.")
if segments[0].count("<b>✳</b>") < 10:
    sys.exit("ERROR: Ticker content is unexpectedly short. No files changed.")

home_after = (home_before[:local_matches[0].start()] +
              ticker + home_before[local_matches[0].end():])

if css_source.count(START) != 1 or css_source.count(END) != 1:
    sys.exit("ERROR: GitHub ticker style markers are invalid. No files changed.")
style = css_source[css_source.index(START):css_source.index(END)+len(END)]
if "transform:translateX(-50%)" not in style or "64s linear infinite" not in style:
    sys.exit("ERROR: GitHub ticker animation is incomplete. No files changed.")

if START in css_before or END in css_before:
    if css_before.count(START) != 1 or css_before.count(END) != 1:
        sys.exit("ERROR: Current ticker CSS markers are incomplete. No files changed.")
    a = css_before.index(START)
    b = css_before.index(END, a) + len(END)
    css_after = css_before[:a] + style + css_before[b:]
else:
    css_after = css_before.rstrip() + "\n\n" + style + "\n"

# Make the browser load the modified stylesheet without erasing other SEO tags.
version = sha256(css_after.encode("utf-8")).hexdigest()[:12]
home_after, count = re.subn(
    r'href="/static/site\.css(?:\?[^"]*)?"',
    'href="/static/site.css?v=seamless-ticker-' + version + '"',
    home_after, count=1
)
if count != 1:
    sys.exit("ERROR: Homepage stylesheet link not found. No files changed.")

# Validate invariants before editing.
if 'rel="canonical"' not in home_after:
    sys.exit("ERROR: SEO canonical missing; no changes made.")
if "<title>Reboot Syndicate | " not in home_after:
    sys.exit("ERROR: Brand-first page title missing; no changes made.")
if 'class="agency-hero-photo"' not in home_after:
    sys.exit("ERROR: Hero photo section missing; no changes made.")
if "R/S service image hover-only visibility" not in css_after:
    sys.exit("ERROR: Existing service hover styles missing; no changes made.")

if home_after != home_before or css_after != css_before:
    backup_dir = ROOT / "backups" / (
        "seamless-ticker-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    )
    for original in (HOME, CSS):
        copy_to = backup_dir / original.relative_to(ROOT)
        copy_to.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, copy_to)
    HOME.write_text(home_after, encoding="utf-8")
    CSS.write_text(css_after, encoding="utf-8")
    print("Backups:", backup_dir)
else:
    print("Ticker already updated.")

print("Running ticker has two matching repeated tracks; no blank trailing edge.")
print("Rebuilding only Reboot Syndicate website...")
subprocess.run(
    ["docker", "compose", "up", "-d", "--build", "website"],
    cwd=ROOT, check=True
)

# Check actual files in rebuilt Docker image; do not race HTTP startup.
verify = r"""
from pathlib import Path
import re
home = Path('/srv/app/templates/index.html').read_text()
css = Path('/srv/app/static/site.css').read_text()
ticker = re.search(r'<div class="ticker" aria-hidden="true">.*?</div></div>', home, re.S)
assert ticker, 'Ticker not in homepage'
segments = re.findall(r'<span class="ticker-segment">(.*?)</span>', ticker.group(), re.S)
assert len(segments) == 2 and segments[0] == segments[1]
start = '/* R/S seamless orange services ticker */'
end = '/* End R/S seamless orange services ticker */'
assert css.count(start) == css.count(end) == 1
style = css[css.index(start):css.index(end)]
assert 'transform:translateX(-50%)' in style
assert '64s linear infinite' in style
assert 'seamless-ticker-' in home
print('PASS: Orange service ticker loops seamlessly, with no end gap.')
"""
checked = subprocess.run(
    ["docker", "compose", "exec", "-T", "website", "python", "-c", verify],
    cwd=ROOT, capture_output=True, text=True
)
if checked.returncode:
    sys.exit("ERROR: Docker ticker verification failed:\n" +
             checked.stdout + checked.stderr)
print(checked.stdout.strip())
print("Hard refresh the homepage with Ctrl+Shift+R.")
