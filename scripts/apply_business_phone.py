#!/usr/bin/env python3
"""Add Reboot Syndicate's Google Voice contact number to a deployed checkout.

Only patches phone-related markup/styles, leaving locally customized hero,
forms, Docker configuration, and all other services unchanged.
"""
from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
PHONE = '(321) 291-3097'
HREF = 'tel:+13212913097'
stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
backup = ROOT / 'backups' / ('phone-update-' + stamp)

def patch(relative, changes):
    path = ROOT / relative
    if not path.is_file():
        print('Skipping missing:', relative)
        return
    original = path.read_text(encoding='utf-8')
    data = original
    for old, new in changes:
        if new in data:
            continue
        if old not in data:
            print('Skipped unmatched section:', relative, old[:55])
            continue
        data = data.replace(old, new, 1)
    if data != original:
        (backup / path.parent.relative_to(ROOT)).mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup / relative)
        path.write_text(data, encoding='utf-8')
        print('Updated:', relative)
    else:
        print('Already current / unchanged:', relative)

new_right = '<div class="rs-top-actions"><a class="rs-phone-top" href="'+HREF+'">CALL / '+PHONE+'</a><span class="live"><i></i> LET\'S BUILD YOUR NEXT MOVE</span></div></div>'
old_right = '<span class="live"><i></i> LET\'S BUILD YOUR NEXT MOVE</span></div>'
patch('app/templates/index.html', [
    (old_right, new_right),
    ('<div class="contact-aside">', '<div class="rs-call-contact"><span>WANNA TALK FIRST?</span><a href="'+HREF+'">'+PHONE+' ↗</a><small>CALL REBOOT SYNDICATE</small></div><div class="contact-aside">'),
    ('<a href="#request">WORK WITH US ↗</a><small>', '<a class="rs-footer-phone" href="'+HREF+'">CALL '+PHONE+' ↗</a><a href="#request">WORK WITH US ↗</a><small>')
])
patch('app/templates/marketing_detail.html', [
    (old_right, new_right),
    ('<div class="agency-detail-micro">','<a class="rs-detail-phone" href="'+HREF+'">PREFER TO CALL? '+PHONE+' ↗</a><div class="agency-detail-micro">')
])
patch('app/templates/marketing.html', [
    ('<span>DIGITAL MARKETING & BUSINESS SOLUTIONS</span></div>', '<div class="rs-top-actions"><a class="rs-phone-top" href="'+HREF+'">CALL / '+PHONE+'</a><span>DIGITAL MARKETING & BUSINESS SOLUTIONS</span></div></div>'),
    ('<a class="marketing-feature-button" href="/#request">','<p class="rs-marketing-call">PREFER A PHONE CALL? <a href="'+HREF+'">'+PHONE+' ↗</a></p><a class="marketing-feature-button" href="/#request">')
])
css = ROOT / 'app/static/site.css'
marker = '/* Reboot Syndicate business phone number / Google Voice */'
if css.is_file() and marker not in css.read_text(encoding='utf-8'):
    (backup / 'app/static').mkdir(parents=True, exist_ok=True)
    shutil.copy2(css, backup / 'app/static/site.css')
    css.write_text(css.read_text(encoding='utf-8') + """
""" + marker + """
.rs-top-actions{display:flex;align-items:center;gap:22px;flex-wrap:wrap;justify-content:flex-end}
.rs-phone-top,.rs-detail-phone,.rs-footer-phone{color:var(--accent)!important}
.rs-phone-top:hover,.rs-detail-phone:hover,.rs-footer-phone:hover,.rs-call-contact>a:hover{text-decoration:underline}
.rs-call-contact{display:flex;flex-direction:column;align-items:flex-start;gap:7px;margin:30px 0 0;padding:22px 24px;border:1px solid #526064;background:#192226}
.rs-call-contact>span,.rs-call-contact>small{font:10px 'DM Mono',monospace;letter-spacing:.08em;color:#bdc7c1}
.rs-call-contact>a{font:900 clamp(31px,3vw,45px)/1 'Barlow Condensed',Impact,sans-serif;color:var(--accent)}
.rs-detail-phone{display:inline-block;margin-bottom:22px;font:800 12px 'DM Mono',monospace}
.rs-marketing-call{font:12px 'DM Mono',monospace;margin:36px 0 14px}
.rs-marketing-call a{color:var(--accent);text-decoration:underline}
@media(max-width:690px){.topline{flex-wrap:wrap}.rs-top-actions{gap:9px 16px;justify-content:flex-start}}
""", encoding='utf-8')
    print('Updated: app/static/site.css')
print('Complete. Original modified files saved under', backup if backup.exists() else 'no backup required')
