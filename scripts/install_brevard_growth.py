#!/usr/bin/env python3
"""Narrow, backed-up update preserving server-specific files and settings."""
import argparse, ast, re, shutil, subprocess, time
from datetime import datetime, timezone
from pathlib import Path
REF = 'origin/improve-brevard-visibility'
NEW = ('app/growth.py','app/templates/growth_work.html','app/templates/growth_pricing.html')
LINKS = '<p data-rs-growth-links><a href="/work">EXPLORE OUR WORK ↗</a> · <a href="/pricing">VIEW STARTING PRICES ↗</a> · <a href="/brevard-county">BREVARD COUNTY SERVICES ↗</a></p>'
def changes(root, source):
    updates = {p: source(p) for p in NEW}
    for p in ('app/main.py','app/seo.py','app/templates/index.html','app/templates/brevard_county.html'):
        s = (root / p).read_text()
        if p.endswith('main.py'):
            if 'from app.growth import router as growth_router' not in s:
                s += '\nfrom app.growth import router as growth_router\napp.include_router(growth_router)\n'
        elif p.endswith('seo.py'):
            if '"/work", "/pricing"' not in s:
                needle = '["/", "/marketing", "/brevard-county"]'
                if s.count(needle) != 1: raise ValueError('Sitemap differs; no files changed.')
                s = s.replace(needle,'["/", "/marketing", "/brevard-county", "/work", "/pricing"]')
        elif p.endswith('index.html'):
            title = 'Brevard County Web Design &amp; Digital Marketing | Reboot Syndicate'
            s, n = re.subn(r'<title>.*?</title>','<title>'+title+'</title>',s,count=1)
            if n != 1: raise ValueError('Homepage title absent.')
            s = re.sub(r'<meta property="og:title"[^>]*>','<meta property="og:title" content="'+title+'">',s)
            intro = 'Reboot Syndicate is an independent web design and digital marketing studio based in Mims, Florida, serving businesses across Brevard County. Build a clearer website, improve local search visibility and connect your marketing with practical automation. Explore our services, starting prices and founder-built projects.'
            s,n = re.subn(r'(<h1 id="hero-title">.*?</h1>\s*)<p>.*?</p>',lambda m:m[1]+'<p>'+intro+'</p>',s,count=1,flags=re.S)
            if n != 1: raise ValueError('Homepage hero differs; no files changed.')
            if 'data-rs-growth-links' not in s:
                s = s.replace('<div class="agency-hero-stats">',LINKS+'<div class="agency-hero-stats">',1)
            if 'data-rs-growth-links' not in s: raise ValueError('Homepage link placement failed.')
        else:
            s = s.replace('YOUR LOCAL BUSINESS.<br><em>MORE VISIBLE ONLINE.</em>','BREVARD COUNTY WEB DESIGN.<br><em>LOCAL SEO &amp; MARKETING.</em>')
            if 'data-rs-growth-links' not in s:
                s = s.replace('<div class="agency-local-actions">',LINKS+'<div class="agency-local-actions">',1)
        updates[p] = s
    for p,s in updates.items():
        if p.endswith('.py'): ast.parse(s)
    return updates

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-dir',type=Path)
    parser.add_argument('--no-build',action='store_true')
    args=parser.parse_args(); root=Path.cwd()
    if not (root/'docker-compose.yml').is_file(): raise SystemExit('Run from ~/reboot-syndicate.')
    def source(p):
        return (args.source_dir/p).read_text() if args.source_dir else subprocess.check_output(['git','show',REF+':'+p],text=True)
    updates=changes(root,source)
    updates={p:s for p,s in updates.items() if not (root/p).exists() or (root/p).read_text()!=s}
    backup=root/'backups'/('brevard-growth-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f'))
    existed={p:(root/p).exists() for p in updates}
    for p in updates:
        if existed[p]:
            (backup/p).parent.mkdir(parents=True,exist_ok=True); shutil.copy2(root/p,backup/p)
    try:
        for p,s in updates.items(): (root/p).write_text(s)
        if not args.no_build:
            subprocess.run(['docker','compose','up','-d','--build','website'],check=True)
            check="import urllib.request; paths=['/','/brevard-county','/work','/pricing','/sitemap.xml']; [urllib.request.urlopen('http://127.0.0.1:8000'+p,timeout=10).read() for p in paths]; print('All five updated routes passed')"
            for attempt in range(10):
                if subprocess.run(['docker','compose','exec','-T','website','python','-c',check]).returncode==0: break
                time.sleep(2)
            else: raise RuntimeError('Route checks failed')
    except Exception:
        for p in updates:
            if existed[p]: shutil.copy2(backup/p,root/p)
            else: (root/p).unlink(missing_ok=True)
        if not args.no_build: subprocess.run(['docker','compose','up','-d','--build','website'],check=False)
        raise
    print(f'Updated {len(updates)} files. Backup: {backup}')
if __name__=='__main__': main()
