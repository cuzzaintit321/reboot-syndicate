#!/usr/bin/env python3
"""Safely enable clickable nested cards across all Reboot Syndicate services.

Run in ~/reboot-syndicate on yeet after fetching origin/main.
Copies only specific card sections from GitHub. Does not overwrite the local
hero, service photos, user customizations, Docker settings or customer data.
"""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path.cwd()
CSS = "app/static/site.css"
PAGE = "app/templates/marketing_detail.html"
if not (ROOT / "docker-compose.yml").is_file() or not (ROOT / CSS).is_file():
    sys.exit("ERROR: Run from ~/reboot-syndicate on yeet.")

def upstream(path):
    r = subprocess.run(
        ["git", "show", "origin/main:" + path], cwd=ROOT, capture_output=True
    )
    if r.returncode:
        sys.exit("ERROR: GitHub source unavailable for " + path +
                 ". Run git fetch origin main. No changes made.")
    return r.stdout.decode("utf-8")

def local(path):
    file = ROOT / path
    if not file.is_file():
        sys.exit("ERROR: Missing local file " + path + ". No changes made.")
    return file.read_text(encoding="utf-8")

def replace_section(local_text, github_text, start, end, label):
    def bounds(s):
        if s.count(start) != 1:
            sys.exit("ERROR: Missing or repeated " + label + ". No changes made.")
        a = s.index(start)
        b = s.find(end, a + len(start))
        if b < 0:
            sys.exit("ERROR: Cannot find end of " + label + ". No changes made.")
        return a, b
    a, b = bounds(local_text)
    c, d = bounds(github_text)
    return local_text[:a] + github_text[c:d] + local_text[b:]

template = local(PAGE)
source = upstream(PAGE)
# Replace only the starting price panel, not the surrounding local hero.
upstream_price = re.search(r'<a class="agency-detail-price".*?</a>', source, re.S)
local_price = re.search(r'<(?:a|div) class="agency-detail-price".*?</(?:a|div)>', template, re.S)
if not upstream_price or not local_price:
    sys.exit("ERROR: Price card markup differs. No changes made.")
template = (template[:local_price.start()] + upstream_price.group()
            + template[local_price.end():])

# Update the repeated card templates, which render automatically for all 14
# separate service pages. Preserve the rest of each section.
template = replace_section(
    template, source, '  <div class="agency-detail-feature-grid">',
    '\n</section>', "WHAT WE DO feature grid"
)
template = replace_section(
    template, source, '    <ul class="agency-detail-checks">',
    '    </ul>', "deliverables"
)
template = replace_section(
    template, source, '    {% for item in service.bestFor %}',
    '    {% endfor %}', "WHO THIS IS FOR items"
)
template = replace_section(
    template, source, '  <div class="agency-detail-steps">',
    '\n</section>', "process cards"
)

if template.count('<details class="agency-detail-feature">') != 1:
    sys.exit("ERROR: Feature card template mismatch. No changes made.")
if template.count('<details class="agency-detail-step">') != 3:
    sys.exit("ERROR: Expected 3 interactive process cards. No changes made.")
for needle in (
    '<details class="agency-detail-deliverable">',
    '<details class="agency-detail-fit-item">',
    '<a class="agency-detail-price"',
):
    if needle not in template:
        sys.exit("ERROR: Missing interactive markup: " + needle + ". No changes made.")

css = local(CSS)
css_source = upstream(CSS)
marker = "/* R/S clickable nested cards and service details (all service pages) */"
accessibility_marker = "/* R/S accessible labels inside clickable nested tiles */"
if marker not in css_source or accessibility_marker not in css_source:
    sys.exit("ERROR: Latest GitHub styles are incomplete. No changes made.")
if marker not in css:
    css = css.rstrip() + "\n\n" + css_source[css_source.index(marker):].strip() + "\n"
elif accessibility_marker not in css:
    css = css.rstrip() + "\n\n" + css_source[css_source.index(accessibility_marker):].strip() + "\n"

changes = {PAGE: template, CSS: css}
style_version = sha256(css.encode("utf-8")).hexdigest()[:12]
for path in (
    "app/templates/index.html",
    "app/templates/marketing_detail.html",
    "app/templates/marketing.html",
    "app/templates/brevard_county.html",
):
    if not (ROOT / path).is_file():
        continue
    current = changes[path] if path in changes else local(path)
    changed, matches = re.subn(
        r'href="/static/site\.css(?:\?[^"]*)?"',
        'href="/static/site.css?v=all-cards-' + style_version + '"',
        current, count=1
    )
    if matches != 1:
        sys.exit("ERROR: Stylesheet link not found in " + path + ". No changes made.")
    changes[path] = changed

if 'Marketing and advertising outcomes vary.' in changes.get("app/templates/index.html", ""):
    sys.exit("ERROR: Removed footer sentence reappeared; no changes made.")
if 'agency-hero-photo' not in changes.get("app/templates/index.html", ""):
    sys.exit("ERROR: Homepage hero markup missing; no changes made.")
if 'R/S service image hover-only visibility' not in changes[CSS]:
    sys.exit("ERROR: Existing tile hover rules missing; no changes made.")

backup_root = ROOT / "backups" / (
    "all-clickable-tiles-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f")
)
changed_count = 0
for path, content in changes.items():
    target = ROOT / path
    original = target.read_text(encoding="utf-8") if target.is_file() else None
    if original == content:
        print("Already up to date:", path)
        continue
    if original is not None:
        backup = backup_root / path
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, backup)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    changed_count += 1
    print("Updated:", path)

print("Modified files:", changed_count)
print("Backups:", backup_root if backup_root.is_dir() else "not needed")
print("Rebuilding only Reboot Syndicate website...")
subprocess.run(["docker", "compose", "up", "-d", "--build", "website"], check=True)

# Verify inside Docker directly; avoid race conditions during app startup.
check = r"""
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
page = Path('/srv/app/templates/marketing_detail.html').read_text()
css = Path('/srv/app/static/site.css').read_text()
assert page.count('<details class="agency-detail-feature">') == 1
assert '<details class="agency-detail-deliverable">' in page
assert '<details class="agency-detail-fit-item">' in page
assert page.count('<details class="agency-detail-step">') == 3
assert '<a class="agency-detail-price"' in page
assert 'R/S clickable nested cards and service details' in css
assert 'R/S service image hover-only visibility' in css
assert 'R/S accessible labels inside clickable nested tiles' in css
env = Environment(loader=FileSystemLoader('/srv/app/templates'))
env.get_template('marketing_detail.html')
print('PASS: Clickable feature, deliverable, fit, process and pricing cards installed.')
"""
result = subprocess.run(
    ["docker", "compose", "exec", "-T", "website", "python", "-c", check],
    text=True, capture_output=True
)
if result.returncode:
    sys.exit("ERROR: Docker verification failed:\n" + result.stdout + result.stderr)
print(result.stdout.strip())
print("Hard-refresh a service detail page with Ctrl+Shift+R.")
