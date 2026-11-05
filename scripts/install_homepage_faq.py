#!/usr/bin/env python3
"""Add only a compact homepage FAQ, preserving all existing copy and layout."""
from pathlib import Path
from datetime import datetime, timezone
import re
import shutil
import subprocess
import time

STYLE = '''<!-- RS FAQ STYLE START -->
<style id="rs-home-faq-style">
#rs-home-faq{padding-top:55px;padding-bottom:55px;border-top:1px solid #344247}
#rs-home-faq .rs-faq-inner{max-width:960px;margin:auto}
#rs-home-faq h2{font:900 clamp(32px,5vw,58px)/1.05 'Barlow Condensed',Impact,sans-serif;margin:14px 0 26px}
#rs-home-faq details{border-top:1px solid #344247}
#rs-home-faq details:last-child{border-bottom:1px solid #344247}
#rs-home-faq summary{display:flex;justify-content:space-between;align-items:center;gap:20px;cursor:pointer;list-style:none;padding:20px 0;font-size:17px;font-weight:700;line-height:1.5;color:#e8ebe6}
#rs-home-faq summary::-webkit-details-marker{display:none}
#rs-home-faq summary::after{content:'+';color:var(--accent,#ff5a24);font-size:25px;flex-shrink:0}
#rs-home-faq details[open]>summary::after{content:'−'}
#rs-home-faq summary:focus-visible{outline:2px solid var(--accent,#ff5a24);outline-offset:4px}
#rs-home-faq p{color:#bfccc5;font-size:16px;line-height:1.8;margin:0;padding:0 0 22px;max-width:800px}
#rs-home-faq a{color:var(--accent,#ff5a24);text-decoration:underline;text-underline-offset:3px}
@media(max-width:600px){#rs-home-faq{padding-top:35px;padding-bottom:35px}#rs-home-faq summary{font-size:16px;gap:12px}}
</style>
<!-- RS FAQ STYLE END -->'''
FAQ = '''<!-- RS FAQ START -->
<section class="section-wrap" id="rs-home-faq" aria-labelledby="rs-home-faq-title">
<div class="rs-faq-inner"><span class="section-index">BEFORE WE GET STARTED</span>
<h2 id="rs-home-faq-title">QUESTIONS? STRAIGHT ANSWERS.</h2>
<details><summary>What can Reboot Syndicate help my business with?</summary><p>We connect website design, SEO, social media, digital advertising and automation. Start with a single project or discuss ongoing support based on your goals. Explore our <a href="/#services">services and starting prices</a> to see which options fit.</p></details>
<details><summary>Do you work with businesses throughout Brevard County?</summary><p>Yes. We provide web design and digital marketing for businesses across Brevard County and the Space Coast. Digital projects can also be delivered remotely beyond the county. See our <a href="/brevard-county">Brevard County services</a> for more information.</p></details>
<details><summary>How much does a business website cost?</summary><p>Our <a href="/marketing/website-design">website design page</a> shows the starting price and typical deliverables. Your quote depends on the page count, content, custom features and integrations. Hosting, maintenance and third-party services are discussed separately or included in an agreed plan. We confirm the scope and fees before work begins.</p></details>
<details><summary>Can you improve my existing website?</summary><p>Often, yes. We review the current platform, mobile layout, content and contact options before recommending targeted improvements or a rebuild. Share your website and explain what is not working so we can discuss a practical next step.</p></details>
<details><summary>What is the difference between local SEO and paid ads?</summary><p><a href="/marketing/local-seo">Local SEO</a> improves your website's relevance and discoverability for searches related to your services and area. <a href="/marketing/digital-advertising">Paid advertising</a> uses a separate advertising budget to reach an audience through sponsored placements. Neither guarantees customers or a particular search ranking.</p></details>
<details><summary>What do you need to get started?</summary><p>Tell us what your business offers, who you serve and what you want to improve. Include your existing website if you have one, along with your preferred budget and timeline. <a href="/#request">Request a consultation</a> and we will discuss the scope before any paid work begins.</p></details>
</div></section>
<!-- RS FAQ END -->'''

def transform(text):
    # Update our own bounded blocks on repeat runs; never replace other sections.
    if '<!-- RS FAQ START -->' in text:
        text,n = re.subn(r'<!-- RS FAQ START -->.*?<!-- RS FAQ END -->',lambda _:FAQ,text,flags=re.S)
        if n != 1: raise ValueError('Unexpected FAQ markers; nothing changed.')
    else:
        matches=list(re.finditer(r'<section\b[^>]*\bid=["\']request["\'][^>]*>',text))
        if len(matches)!=1: raise ValueError('Contact section not found uniquely; nothing changed.')
        pos=matches[0].start(); text=text[:pos]+FAQ+'\n'+text[pos:]
    if '<!-- RS FAQ STYLE START -->' in text:
        text,n=re.subn(r'<!-- RS FAQ STYLE START -->.*?<!-- RS FAQ STYLE END -->',lambda _:STYLE,text,flags=re.S)
        if n!=1: raise ValueError('Unexpected style markers; nothing changed.')
    else:
        if text.count('</head>')!=1: raise ValueError('Expected one head; nothing changed.')
        text=text.replace('</head>',STYLE+'\n</head>',1)
    return text

def main():
    page=Path('app/templates/index.html')
    if not page.exists() or not Path('docker-compose.yml').exists():
        raise SystemExit('Run from ~/reboot-syndicate.')
    before=page.read_text(); after=transform(before)
    if before==after:
        print('FAQ already installed; rebuilding and checking the current site.')
    backup=Path('backups')/('homepage-faq-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f'))
    backup.mkdir(parents=True);shutil.copy2(page,backup/'index.html')
    try:
        page.write_text(after)
        subprocess.run(['docker','compose','up','-d','--build','website'],check=True)
        check="import urllib.request; s=urllib.request.urlopen('http://127.0.0.1:8000/',timeout=10).read().decode(); assert 'id=\"rs-home-faq\"' in s; assert s.count('<summary>')>=6"
        for attempt in range(15):
            r=subprocess.run(['docker','compose','exec','-T','website','python','-c',check],capture_output=True,text=True)
            if r.returncode==0: break
            time.sleep(2)
        else: raise RuntimeError('Homepage check failed: '+r.stderr[-1000:])
    except Exception:
        shutil.copy2(backup/'index.html',page)
        subprocess.run(['docker','compose','up','-d','--build','website'],check=False)
        raise
    print('FAQ installed; homepage check passed. Backup: '+str(backup))

if __name__=='__main__':main()
