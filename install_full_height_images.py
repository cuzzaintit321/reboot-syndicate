#!/usr/bin/env python3
"""Replace only Reboot Syndicate card photos and their hover rules."""
from pathlib import Path
import shutil
from datetime import datetime
root=Path(__file__).resolve().parent
css=root/'app/static/site.css'
html=root/'app/templates/index.html'
assets=root/'replacement_images'
destination=root/'app/static/images'
slugs=['website-design', 'local-seo', 'google-business-profile', 'social-media', 'digital-advertising', 'lead-automation', 'branding-design', 'content-marketing', 'email-sms', 'reputation-management', 'ecommerce', 'analytics-conversion', 'business-technology', 'it-support']
if not css.is_file() or not html.is_file() or 'agency-service-card' not in html.read_text():
    raise SystemExit('Agency homepage or stylesheet missing. No changes made.')
missing=[s for s in slugs if not (assets/(s+'.webp')).is_file()]
if missing: raise SystemExit('Missing: '+', '.join(missing))
backup=root/'backups'/('full-height-hover-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True,exist_ok=True)
shutil.copy2(css,backup/'site.css')
destination.mkdir(parents=True,exist_ok=True)
for s in slugs:
    old=destination/(s+'.webp')
    if old.is_file():shutil.copy2(old,backup/old.name)
    shutil.copy2(assets/old.name,old)

start='/* REBOOT_FULL_HEIGHT_HOVER_START */'
end='/* REBOOT_FULL_HEIGHT_HOVER_END */'
css_patch="""
/* REBOOT_FULL_HEIGHT_HOVER_START */
/* Hover photo fills the entire card, rather than making a short image strip. */
.agency-service-card{position:relative!important;isolation:isolate;overflow:hidden;background:#151d20!important}
.agency-service-card::before{
 content:""!important;position:absolute!important;inset:0!important;
 top:0!important;left:0!important;width:100%!important;height:100%!important;
 z-index:0!important;display:block!important;
 background-image:linear-gradient(180deg,rgba(6,10,12,.38),rgba(6,10,12,.79)),var(--card-photo)!important;
 background-position:center!important;background-size:cover!important;
 background-repeat:no-repeat!important;
 opacity:0!important;pointer-events:none!important;transition:opacity .3s ease!important;
}
.agency-service-card:is(:hover,:focus-visible)::before{opacity:1!important}
.agency-service-card > *:not(.agency-card-image){position:relative;z-index:1}
.agency-service-card > .agency-card-image{display:none!important}
.agency-service-card:is(:hover,:focus-visible) h3{color:#fff}
.agency-service-card:is(:hover,:focus-visible) p{color:#e9eeeb}
/* REBOOT_SERVICE_IMAGE_VARIABLES */
@media(prefers-reduced-motion:reduce){.agency-service-card::before{transition:none!important}}
/* REBOOT_FULL_HEIGHT_HOVER_END */
"""
rules='\n'.join('.agency-service-card[href="/marketing/%s"]{--card-photo:url("/static/images/%s.webp")}'%(s,s) for s in slugs)
css_patch=css_patch.replace('/* REBOOT_SERVICE_IMAGE_VARIABLES */',rules)
old=css.read_text()
if start in old and end in old:
    old=old[:old.index(start)]+old[old.index(end)+len(end):]
css.write_text(old.rstrip()+'\n\n'+css_patch)
print('Replaced 14 card photos. Original images and CSS backed up in:',backup)
print('No other website files or configuration were changed.')
