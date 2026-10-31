#!/usr/bin/env python3
"""Install original service images as hover-only backgrounds, preserving website backend."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSS = ROOT / 'app/static/site.css'
HTML = ROOT / 'app/templates/index.html'
RULES = ROOT / 'hover_images.css'
SLUGS = ['website-design', 'local-seo', 'google-business-profile', 'social-media', 'digital-advertising', 'lead-automation', 'branding-design', 'content-marketing', 'email-sms', 'reputation-management', 'ecommerce', 'analytics-conversion', 'business-technology', 'it-support']
if not CSS.is_file() or not HTML.is_file():
    raise SystemExit('Run this script inside the Reboot Syndicate project root.')
page = HTML.read_text(encoding='utf-8')
missing_cards = [slug for slug in SLUGS if f'href="/marketing/{slug}"' not in page]
if missing_cards or 'agency-service-card' not in page:
    raise SystemExit('Unexpected homepage: missing service cards '+', '.join(missing_cards))
missing_images = [slug for slug in SLUGS if not (ROOT / f'app/static/images/{slug}.webp').is_file()]
if missing_images:
    raise SystemExit('Image files missing: '+', '.join(missing_images))
original = CSS.read_text(encoding='utf-8')
if 'reveal each service image on hover only' in original:
    print('Hover effects already installed; no CSS changes needed.')
else:
    CSS.write_text(original.rstrip()+'\n\n'+RULES.read_text(encoding='utf-8'),encoding='utf-8')
    print('Hover-only service images installed in site.css.')
print('Verified', len(SLUGS), 'service images. Rebuild with: docker compose up -d --build website')
