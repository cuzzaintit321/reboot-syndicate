#!/usr/bin/env python3
"""Safely install search discovery and local SEO without overwriting other edits.
Run from ~/reboot-syndicate on yeet after git fetch origin main.
"""
from datetime import datetime
from pathlib import Path
import ast
import re
import shutil
import subprocess
import sys

ROOT = Path.cwd()
if not (ROOT / "docker-compose.yml").is_file():
    sys.exit("ERROR: Run from ~/reboot-syndicate on yeet")

def github(path):
    r = subprocess.run(["git", "show", "origin/main:" + path], capture_output=True, cwd=ROOT)
    if r.returncode:
        sys.exit("ERROR: GitHub version missing: " + path + ". Run git fetch origin main.")
    return r.stdout.decode("utf-8")

def local(path):
    target = ROOT / path
    if not target.is_file():
        sys.exit("ERROR: Local file missing: " + path)
    return target.read_text(encoding="utf-8")

def metadata(local_text, github_text, path):
    # Preserve all local markup and the stylesheet URL, which may have a version.
    pattern = re.compile(r'<meta name="description"[^>]*>.*?(?=<link rel="stylesheet")', re.S | re.I)
    a, b = list(pattern.finditer(local_text)), list(pattern.finditer(github_text))
    if len(a) != 1 or len(b) != 1 or 'rel="canonical"' not in b[0].group():
        sys.exit("ERROR: SEO head differs in " + path + "; no changes made.")
    return local_text[:a[0].start()] + b[0].group() + local_text[a[0].end():]

changes = {
    "app/seo.py": github("app/seo.py"),
    "app/templates/brevard_county.html": github("app/templates/brevard_county.html"),
}
p = "app/main.py"
s = local(p)
if "from app.seo import router as seo_router" not in s:
    needle = "from app.marketing_services import router as marketing_router\n"
    if needle not in s:
        sys.exit("ERROR: Marketing router import absent; no changes made.")
    s = s.replace(needle, needle + "from app.seo import router as seo_router\n", 1)
if "app.include_router(seo_router)" not in s:
    needle = "app.include_router(marketing_router)"
    if needle not in s:
        sys.exit("ERROR: Marketing router registration absent; no changes made.")
    s = s.replace(needle, needle + "\napp.include_router(seo_router)", 1)
changes[p] = s

p = "app/marketing_services.py"
s = local(p)
u = github(p)
start = u.find("SEO_METADATA = {")
end = u.find("@router.get('/marketing/{slug}')", start)
route = s.find("@router.get('/marketing/{slug}')")
if min(start,end,route) < 0:
    sys.exit("ERROR: SEO metadata or service route missing; no changes made.")
meta = u[start:end].strip() + "\n\n"
existing_start = s.find("SEO_METADATA = {")
s = (s[:existing_start] if existing_start >= 0 else s[:route]) + meta + s[route:]
anchor = "        'pricing': SERVICE_PRICING[slug],"
for key, val in (
    ("seo_title", "SEO_METADATA[slug]['title']"),
    ("seo_description", "SEO_METADATA[slug]['description']"),
    ("canonical_url", "f'https://rebootsyndicate.com/marketing/{slug}'"),
):
    if "'" + key + "':" not in s:
        if anchor not in s:
            sys.exit("ERROR: Service response differs; no changes made.")
        s = s.replace(anchor, anchor + "\n        '" + key + "': " + val + ",", 1)
changes[p] = s

p = "app/templates/index.html"
s = metadata(local(p), github(p), p)
if 'href="/brevard-county"' not in s:
    match = re.search(r'<section class="agency-about section-wrap" id="about">.*?</section>',s,re.S)
    if not match or "</div></section>" not in match.group():
        sys.exit("ERROR: Homepage about section not found; no changes made.")
    original = match.group()
    addition = ('<p>For businesses on the Space Coast, explore our '
                '<a href="/brevard-county">Brevard County web design, SEO and marketing services</a>.</p>')
    changed = original.replace("</div></section>",addition + "</div></section>",1)
    s = s.replace(original,changed,1)
footer = re.search(r'<footer>.*?</footer>',s,re.S)
if not footer or "<small>" not in footer.group():
    sys.exit("ERROR: Homepage footer differs; no changes made.")
if 'href="/brevard-county"' not in footer.group():
    s = s.replace(footer.group(), footer.group().replace(
        "<small>",'<a href="/brevard-county">BREVARD COUNTY ↗</a><small>',1),1)
changes[p] = s

for p in ("app/templates/marketing_detail.html","app/templates/marketing.html"):
    s = metadata(local(p),github(p),p)
    footer = re.search(r'<footer>.*?</footer>',s,re.S)
    if not footer:
        sys.exit("ERROR: Footer not found in " + p + "; no changes made.")
    if 'href="/brevard-county"' not in footer.group():
        f = footer.group().replace(
            "</footer>",'<a href="/brevard-county">BREVARD COUNTY SERVICES ↗</a></footer>',1)
        s = s.replace(footer.group(),f,1)
    changes[p] = s

p = "app/templates/thanks.html"
s = local(p)
if 'name="robots"' not in s:
    marker = "<title>Request Received | Reboot Syndicate</title>"
    if marker not in s:
        sys.exit("ERROR: Thank-you title missing; no changes made.")
    s = s.replace(marker,'<meta name="robots" content="noindex,follow">' + marker,1)
changes[p] = s

p = "app/static/site.css"
s,u = local(p),github(p)
marker = "/* R/S Brevard County local SEO landing page */"
if marker not in u:
    sys.exit("ERROR: Brevard CSS unavailable; no changes made.")
if marker not in s:
    s = s.rstrip() + "\n\n" + u[u.index(marker):].strip() + "\n"
changes[p] = s

# Validate all files before writing any changes.
for p in ("app/main.py","app/marketing_services.py","app/seo.py"):
    try:
        ast.parse(changes[p], filename=p)
    except SyntaxError as exc:
        sys.exit(f"ERROR: Python error {p}: {exc}. No changes made.")
if "Marketing and advertising outcomes vary." in changes["app/templates/index.html"]:
    sys.exit("ERROR: Unwanted old footer sentence found. No changes made.")
if 'rel="canonical"' not in changes["app/templates/index.html"]:
    sys.exit("ERROR: Canonical tag missing. No changes made.")

backup_root = ROOT / "backups" / ("seo-foundation-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
updated = 0
for p, content in changes.items():
    target = ROOT / p
    old = target.read_text(encoding="utf-8") if target.is_file() else None
    if old == content:
        print("Already correct:",p)
        continue
    if target.is_file():
        backup = backup_root / p
        backup.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(target,backup)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(content,encoding="utf-8")
    print("Updated:",p)
    updated += 1

print("Updated files:",updated)
print("Backups:",backup_root if backup_root.is_dir() else "not needed")
print("Rebuilding only Reboot Syndicate's website...")
subprocess.run(["docker","compose","up","-d","--build","website"],check=True)

# Verify directly inside Docker; don't race Uvicorn HTTP startup.
test = r"""
from app.main import app
from app.marketing_services import SEO_METADATA, SERVICES
from app.seo import sitemap_xml, robots_txt
from xml.etree import ElementTree
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
routes = {r.path for r in app.routes}
assert {'/robots.txt','/sitemap.xml','/brevard-county'} <= routes
assert len(SERVICES)==14 and set(SERVICES)==set(SEO_METADATA)
xml = ElementTree.fromstring(sitemap_xml().body)
locs = [el.text for el in xml.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert len(locs)==17 and len(set(locs))==17
assert 'https://rebootsyndicate.com/brevard-county' in locs
assert 'Sitemap: https://rebootsyndicate.com/sitemap.xml' in robots_txt().body.decode()
env = Environment(loader=FileSystemLoader('/srv/app/templates'))
for name in ('index.html','marketing.html','marketing_detail.html','brevard_county.html','thanks.html'):
    env.get_template(name)
home = Path('/srv/app/templates/index.html').read_text()
assert 'rel="canonical"' in home and 'href="/brevard-county"' in home
assert 'Marketing and advertising outcomes vary.' not in home
css = Path('/srv/app/static/site.css').read_text()
assert 'R/S Brevard County local SEO landing page' in css
assert 'R/S service image hover-only visibility' in css
print('PASS: SEO endpoints, 17 sitemap URLs, 14 service metadata entries and templates verified in Docker.')
"""
result = subprocess.run(
    ["docker","compose","exec","-T","website","python","-c",test],
    capture_output=True,text=True
)
if result.returncode:
    sys.exit("ERROR: Verification failed. Original files backed up.\n"
             + result.stdout + result.stderr)
print(result.stdout.strip())
print("Review /robots.txt, /sitemap.xml and /brevard-county on rebootsyndicate.com")
