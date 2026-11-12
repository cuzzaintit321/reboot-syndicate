#!/usr/bin/env python3
"""Apply brand-first browser titles and full-bleed, single-layer service images.

Run on yeet from ~/reboot-syndicate after git fetch origin main.
Preserves other local edits and backs up all changes before Docker rebuild.
"""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT=Path.cwd()
CSS="app/static/site.css"
PAGES=("index.html","marketing.html","marketing_detail.html",
       "brevard_county.html","service.html","thanks.html","admin.html")
START="/* R/S full-frame service-detail artwork: no more cropped dashboards */"
END="/* End R/S full-frame service-detail artwork */"
if not (ROOT/"docker-compose.yml").is_file():
    sys.exit("ERROR: Run inside ~/reboot-syndicate on yeet.")

def upstream(relative):
    res=subprocess.run(["git","show","origin/main:"+relative],
                       cwd=ROOT,capture_output=True,text=True)
    if res.returncode:
        sys.exit("ERROR: GitHub file unavailable: "+relative)
    return res.stdout

def read(relative):
    target=ROOT/relative
    if not target.is_file():
        sys.exit("ERROR: Local site file missing: "+relative)
    return target.read_text(encoding="utf-8")

changes={}
for filename in PAGES:
    path="app/templates/"+filename
    local=read(path)
    remote=upstream(path)
    titles=list(re.finditer(r"<title>.*?</title>",local,re.S|re.I))
    correct=list(re.finditer(r"<title>.*?</title>",remote,re.S|re.I))
    if len(titles)!=1 or len(correct)!=1:
        sys.exit("ERROR: Missing or multiple title tags on "+filename)
    newtitle=correct[0].group()
    if not newtitle.startswith("<title>Reboot Syndicate | "):
        sys.exit("ERROR: Reference title is not brand first: "+filename)
    local=local[:titles[0].start()]+newtitle+local[titles[0].end():]
    # Match Open Graph branding if this page already exposes it, without
    # altering its description, canonical tag or content.
    pattern=r'<meta\b[^>]*property="og:title"[^>]*>'
    old=list(re.finditer(pattern,local,re.I|re.S))
    new=list(re.finditer(pattern,remote,re.I|re.S))
    if len(old)>1 or len(new)>1:
        sys.exit("ERROR: Duplicate social titles on "+filename)
    if new:
        if old:
            local=local[:old[0].start()]+new[0].group()+local[old[0].end():]
        else:
            marker=re.search(r"</head>",local,re.I)
            if marker is None: sys.exit("ERROR: No closing head on "+filename)
            local=local[:marker.start()]+new[0].group()+"\n"+local[marker.start():]
    changes[path]=local

css=read(CSS)
up=upstream(CSS)
if up.count(START)!=1 or up.count(END)!=1:
    sys.exit("ERROR: Full-bleed CSS marker missing from GitHub.")
patch=up[up.index(START):up.index(END)+len(END)]
if (patch.count("var(--detail-photo)")!=1
    or "background-size:cover,cover;" not in patch
    or "content:none!important;" not in patch):
    sys.exit("ERROR: Full-bleed CSS is invalid.")
if START in css or END in css:
    if css.count(START)!=1 or css.count(END)!=1:
        sys.exit("ERROR: Existing image CSS markers are incomplete.")
    a=css.index(START)
    b=css.index(END,a)+len(END)
    css=css[:a]+patch+css[b:]
else:
    css=css.rstrip()+"\n\n"+patch+"\n"
changes[CSS]=css

p="app/templates/marketing_detail.html"
version=sha256(css.encode()).hexdigest()[:12]
replaced,n=re.subn(
    r'href="/static/site\.css(?:\?[^"]*)?"',
    'href="/static/site.css?v=single-cover-'+version+'"',
    changes[p],count=1
)
if n!=1:
    sys.exit("ERROR: Detail-page stylesheet link not found.")
changes[p]=replaced

if ('href="/brevard-county"' not in changes["app/templates/index.html"]
    or 'rel="canonical"' not in changes["app/templates/index.html"]
    or "R/S service image hover-only visibility" not in css):
    sys.exit("ERROR: Existing SEO or homepage hover styles missing; no changes made.")

backup=ROOT/"backups"/("brand-and-fullbleed-"+datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
count=0
for relative,updated in changes.items():
    target=ROOT/relative
    before=target.read_text(encoding="utf-8")
    if before==updated:
        print("Already correct:",relative)
        continue
    dst=backup/relative
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(target,dst)
    target.write_text(updated,encoding="utf-8")
    print("Updated:",relative)
    count+=1

print("Modified files:",count)
print("Backups:",backup if backup.is_dir() else "not needed")
print("Rebuilding only the website...")
subprocess.run(["docker","compose","up","-d","--build","website"],cwd=ROOT,check=True)
verify=r"""
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
root=Path('/srv/app')
css=(root/'static/site.css').read_text()
start='/* R/S full-frame service-detail artwork: no more cropped dashboards */'
end='/* End R/S full-frame service-detail artwork */'
block=css[css.index(start):css.index(end)]
assert block.count('var(--detail-photo)')==1
assert 'background-size:cover,cover;' in block
assert 'content:none!important;' in block
assert 'background-size:contain;' not in block
env=Environment(loader=FileSystemLoader(str(root/'templates')))
for name in ('index.html','marketing.html','marketing_detail.html','brevard_county.html',
             'service.html','thanks.html','admin.html'):
    page=(root/'templates'/name).read_text()
    assert '<title>Reboot Syndicate | ' in page, name
    env.parse(page)
detail=(root/'templates/marketing_detail.html').read_text()
assert 'site.css?v=single-cover-' in detail
print('PASS: Brand-first page titles and one full-bleed photo on all 14 service pages.')
"""
result=subprocess.run(["docker","compose","exec","-T","website","python","-c",verify],
                      cwd=ROOT,capture_output=True,text=True)
if result.returncode:
    sys.exit("ERROR: Container check failed. Backups are available.\n"+result.stdout+result.stderr)
print(result.stdout.strip())
print("Hard-refresh Firefox with Ctrl+Shift+R.")
