#!/usr/bin/env python3
"""Configure Reboot Syndicate homepage with a Google-compatible PNG favicon.

From ~/reboot-syndicate:
  python3 install_reboot_favicon.py --check
  python3 install_reboot_favicon.py --apply

Backups are stored outside the Git repo; no secrets or database files are read.
"""
import argparse
from pathlib import Path
import re
from datetime import datetime, timezone
import shutil
import subprocess

p = argparse.ArgumentParser(description=__doc__)
m = p.add_mutually_exclusive_group(required=True)
m.add_argument('--check', action='store_true', help='Check local layout and show planned change; do not edit.')
m.add_argument('--apply', action='store_true', help='Update homepage and image, and rebuild only website service.')
args = p.parse_args()
root = Path.cwd()
source = Path(__file__).resolve().parent / 'favicon-192.png'
html = root/'app/templates/index.html'
target = root/'app/static/favicon-192.png'
compose = root/'docker-compose.yml'
if not all(x.is_file() for x in [source,html,compose]):
    raise SystemExit('ERROR: Run from ~/reboot-syndicate with both installer and favicon PNG in this directory.')
if source.read_bytes()[:8] != b'\x89PNG\r\n\x1a\n':
    raise SystemExit('ERROR: Invalid PNG. No changes made.')

original = html.read_text(encoding='utf-8')
# Read all HTML link tags and keep only rel="icon" and rel="shortcut icon".
link_pattern = re.compile(r'<link\b[^>]*>', flags=re.I)
rel_pattern = re.compile(r'''\brel\s*=\s*(["'])(.*?)\1''', flags=re.I | re.S)
positions=[]
for match in link_pattern.finditer(original):
    rel=rel_pattern.search(match.group())
    if rel and rel.group(2).strip().lower() in ('icon','shortcut icon'):
        positions.append((match.start(),match.end(),match.group()))
if not positions:
    raise SystemExit('ERROR: No existing rel="icon" link found in homepage. No changes made; inspect HTML manually.')
newtag='<link rel="icon" type="image/png" sizes="192x192" href="/static/favicon-192.png">'
updated=original
for i,(start,end,tag) in reversed(list(enumerate(positions))):
    updated=updated[:start]+(newtag if i==0 else '')+updated[end:]
if '<head' not in updated.lower() or '</head>' not in updated.lower():
    raise SystemExit('ERROR: Unexpected homepage HTML structure. No changes made.')
print('Homepage:',html)
print('Current icon tags:',*[v[2] for v in positions],sep='\n  ')
print('New icon tag:',newtag)
print('Target image:',target)
if args.check:
    print('DRY RUN PASSED; no changes made.')
    raise SystemExit(0)

# Store backups outside Git repo and do not modify any deployment secrets.
backup= root.parent/'reboot-favicon-backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
backup.mkdir(mode=0o700,parents=True)
shutil.copy2(html,backup/'index.html.before')
if target.exists():
    shutil.copy2(target,backup/'favicon-192.png.before')
try:
    shutil.copy2(source,target)
    html.write_text(updated,encoding='utf-8')
    subprocess.run(['docker','compose','up','-d','--build','--no-deps','website'],cwd=root,check=True)
except Exception:
    shutil.copy2(backup/'index.html.before',html)
    if (backup/'favicon-192.png.before').exists():
        shutil.copy2(backup/'favicon-192.png.before',target)
    else:
        target.unlink(missing_ok=True)
    print('ERROR: Failed; local template and favicon restored. Existing container might have been rebuilt.')
    raise
print('PASS: Homepage uses /static/favicon-192.png (PNG, 192x192).')
print('Backup:',backup)
print('Verify: curl -sSI https://rebootsyndicate.com/static/favicon-192.png | head')
print('Then request homepage indexing in Google Search Console; Google can take days/weeks.')
