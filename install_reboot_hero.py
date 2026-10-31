#!/usr/bin/env python3
"""Replace ONLY the old tilted homepage hero art with a real photo.

Preserves the R/S DIGITAL / GROWTH SYSTEM, ● ONLINE, 01 / DISCOVER,
02 / CREATE, 03 / OPTIMIZE labels and all other site sections.
Run from ~/circuit-syndicate after extracting the included archive.
"""
from pathlib import Path
import datetime, re, shutil, sys

root=Path.cwd()
index=root/'app/templates/index.html'
css=root/'app/static/site.css'
source=root/'reboot-syndicate-hero.webp'
target=root/'app/static/images/reboot-syndicate-hero.webp'
for p in (index, css, source):
    if not p.is_file():
        sys.exit(f'Missing: {p}; run in ~/circuit-syndicate after extracting the ZIP')
html=index.read_text(encoding='utf-8')
styles=css.read_text(encoding='utf-8')
required=('R/S DIGITAL / GROWTH SYSTEM','01 / DISCOVER','02 / CREATE','03 / OPTIMIZE')
if any(label not in html for label in required):
    sys.exit('Expected status or process labels are not present. No changes made.')
new_html=html
if 'class="agency-hero-photo-img"' not in html:
    opening='<div class="agency-hero-right">'
    if html.count(opening)!=1:
        sys.exit('The homepage hero markup differs; no changes made.')
    new_html=html.replace(opening, '<div class="agency-hero-right agency-hero-photo"><img class="agency-hero-photo-img" src="/static/images/reboot-syndicate-hero.webp" alt="Orange-lit marketing studio with strategy, website and analytics displays" fetchpriority="high" decoding="async">',1)
    new_html,count=re.subn(r'<div class="agency-screen">[\s\S]*?(?=<div class="agency-dashboard">)', '',new_html,count=1)
    if count!=1:
        sys.exit('Original tilted artwork was not found; no changes made.')
else:
    new_html=new_html.replace('class="agency-hero-right">','class="agency-hero-right agency-hero-photo">',1)

marker='/* Reboot Syndicate hero photographic panel -- retain status and process labels */'
new_css=styles
if marker not in styles:
    new_css+='''
/* Reboot Syndicate hero photographic panel -- retain status and process labels */
.agency-home .agency-hero-photo{background:#111a1d;isolation:isolate}
.agency-hero-photo-img{position:absolute;inset:0;z-index:0;width:100%;height:100%;display:block;object-fit:cover;object-position:52% 50%;filter:brightness(.82) contrast(1.06);pointer-events:none}
.agency-home .agency-hero-photo::before{z-index:1;opacity:1;background:linear-gradient(180deg,rgba(7,13,15,.88) 0%,transparent 17%,transparent 76%,rgba(7,13,15,.87) 100%);pointer-events:none}
.agency-hero-photo .agency-visual-header,.agency-hero-photo .agency-dashboard{position:relative;z-index:2;background:rgba(10,17,19,.82);backdrop-filter:blur(6px)}
.agency-hero-photo .agency-dashboard{margin-top:auto}
@media(max-width:800px){.agency-hero-photo .agency-hero-photo-img{object-position:center 48%}}
'''
for label in required:
    if label not in new_html:
        sys.exit(f'Protected label missing after changes: {label}; no changes made.')
backup=root/'backups'/('hero-photo-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True,exist_ok=True)
shutil.copy2(index,backup/'index.html')
shutil.copy2(css,backup/'site.css')
if target.exists(): shutil.copy2(target,backup/'reboot-syndicate-hero.webp')
target.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(source,target)
if new_html!=html: index.write_text(new_html,encoding='utf-8')
if new_css!=styles: css.write_text(new_css,encoding='utf-8')
print('Installed new hero photo:',target)
print('Preserved the top and bottom R/S status/process labels.')
print('All unrelated page sections remain untouched.')
print('Backups:',backup)
print('Next: docker compose up -d --build website')
