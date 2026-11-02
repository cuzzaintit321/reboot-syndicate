#!/usr/bin/env python3
"""Install Reboot Syndicate's 15th service: Website Maintenance & Security.

Usage (from ~/reboot-syndicate):
    python3 reboot_add_service_15.py --check
    python3 reboot_add_service_15.py --apply

Affects only the service registry, Stripe server-side catalog, homepage,
marketing overview, shared CSS, and a new vector image. Existing payment,
email, customer and other 14 service implementations are left in place.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import shutil
import sys
import traceback

SLUG = 'website-maintenance'
MARK = 'REBOOT_SERVICE_15'

SERVICE_BLOCK = '''# REBOOT_SERVICE_15_BEGIN
# Service #15: one-site starter maintenance; exact scope agreed in writing.
SERVICES["website-maintenance"] = {
    "name": "Website Maintenance & Security",
    "tag": "KEEP YOUR WEBSITE WORKING.",
    "lead": "Keep your business website in better shape with regular maintenance, backup checks, uptime monitoring and practical security hygiene. Our affordable monthly website care is designed for small sites, with the exact platform, access and tasks confirmed before work begins.",
    "features": [
        ["Website updates", "Review and apply agreed routine website, theme, plugin or software updates on supported platforms, with checks for unexpected changes."],
        ["Backups & recovery readiness", "Check existing backups and recovery options, identify gaps and arrange an appropriate backup process where supported."],
        ["Uptime & SSL monitoring", "Review basic availability and SSL certificate status and flag issues that need attention."],
        ["Security hygiene", "Check common maintenance risks, access practices and known update needs. Security monitoring does not prevent all attacks."],
    ],
    "deliverables": [
        "A documented starter checklist for one agreed business website",
        "Scheduled maintenance and backup checks within supported platforms",
        "Basic availability, SSL and security-hygiene checks where access permits",
        "A plain-language summary of completed work and recommended next steps",
    ],
    "bestFor": [
        "Titusville and Brevard County businesses that want website upkeep",
        "Small businesses with a site but no dedicated technical staff",
        "Owners who want a maintenance partner after a website launch",
    ],
    "faqs": [
        ["What does the $99/month starter plan cover?", "The starting level is for one agreed small-business website with a defined routine maintenance checklist. Hosting, third-party fees, major changes, emergencies and incident response are separate unless explicitly included in a written agreement."],
        ["Does maintenance guarantee my website will never go offline or be hacked?", "No. Backups, updates and monitoring can reduce avoidable risks but cannot guarantee uninterrupted uptime, security or recovery from every incident."],
        ["Can you maintain a site you did not build?", "Often yes. We review the current platform, access, condition and risks before agreeing to work."],
        ["Is there a long-term contract?", "Monthly scope, billing terms and cancellation provisions are provided for review before work begins."],
    ],
    "form": "Website Maintenance / Security",
}
SERVICE_PRICING["website-maintenance"] = {
    "starting": "$99", "unit": "/ mo", "range": "$99+ / mo"
}
SEO_METADATA["website-maintenance"] = {
    "title": "Website Maintenance & Security | Titusville FL | Reboot Syndicate",
    "description": "Website maintenance for Titusville and Brevard County businesses. Routine updates, backups, SSL checks, uptime monitoring and practical security care from $99/month."
}
# The earlier 14-service SEO upgrade uses LOCAL_SEO for page-specific H2s,
# local copy and internal links. Support both pre-upgrade and upgraded sites.
if 'LOCAL_SEO' in globals():
    LOCAL_SEO["website-maintenance"] = {
        "title": SEO_METADATA["website-maintenance"]["title"],
        "description": SEO_METADATA["website-maintenance"]["description"],
        "heading": "WEBSITE CARE",
        "emphasis": "WITHOUT THE GUESSWORK.",
        "copy": "Small businesses in Titusville, Mims and across Brevard County can benefit from scheduled website updates, backup checks, basic uptime and SSL monitoring, and practical security housekeeping. We agree on access and a maintenance checklist for the site before starting. No provider can guarantee zero downtime or complete security.",
        "related": ["website-design", "business-technology", "it-support"],
    }
# REBOOT_SERVICE_15_END

'''

CHECKOUT_BLOCK = '''# REBOOT_SERVICE_15_CHECKOUT
# $99 per month, charged only if a customer actively completes checkout.
CATALOG["website-maintenance"] = ("Website Maintenance & Security", 9900, "subscription")

'''

CARD = '''\n<!-- REBOOT_SERVICE_15_CARD -->
<a class="agency-service-card" href="/marketing/website-maintenance"><div class="agency-service-top"><span>15 / SERVICE</span><strong>CARE</strong></div><h3>Website Maintenance &amp; Security</h3><p>Routine updates, backups, uptime checks and practical website security care.</p><span class="agency-card-pricing"><span class="agency-card-pricing-label">STARTING AT</span><strong>$99<small> / mo</small></strong></span><span class="agency-arrow">EXPLORE SERVICE ↗</span></a>'''

OVERVIEW = '''\n<!-- REBOOT_SERVICE_15_OVERVIEW -->
<a href="/marketing/website-maintenance" class="marketing-service"><b>15 /</b><h3>WEBSITE MAINTENANCE &amp; SECURITY</h3><p>Monthly website updates, backups, uptime and SSL checks, and practical security maintenance for small businesses.</p></a>'''

FORM_OPTION = '<option value="Website Maintenance / Security">Website Maintenance &amp; Security</option>'

STYLE = '''\n/* REBOOT_SERVICE_15_STYLES */
.agency-home .agency-service-card[href="/marketing/website-maintenance"] {
  --card-photo: url('/static/images/website-maintenance.svg');
}
/* Make sure the final card fills the same third-column cell as the other tiles. */
.agency-home .agency-service-card[href="/marketing/website-maintenance"]::before {
  background-size: cover, cover;
  background-position: center, center;
}
'''

IMAGE = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1000" role="img" aria-labelledby="title desc">
<title id="title">Website maintenance and security dashboard</title>
<desc id="desc">Dark technology workstation illustration with website health dashboard, secure shield, server checks and orange status lights.</desc>
<defs>
 <linearGradient id="bg" x2="1" y2="1"><stop stop-color="#0b1014"/><stop offset=".55" stop-color="#17252a"/><stop offset="1" stop-color="#070c10"/></linearGradient>
 <linearGradient id="screen" x2="1" y2="1"><stop stop-color="#26383c"/><stop offset="1" stop-color="#10191d"/></linearGradient>
 <radialGradient id="glow"><stop stop-color="#ed672f" stop-opacity=".25"/><stop offset="1" stop-color="#ed672f" stop-opacity="0"/></radialGradient>
 <filter id="shadow"><feDropShadow dx="0" dy="22" stdDeviation="30" flood-opacity=".6"/></filter>
</defs>
<rect width="1600" height="1000" fill="url(#bg)"/>
<circle cx="1230" cy="400" r="610" fill="url(#glow)"/>
<g opacity=".14" stroke="#a9bdb7" stroke-width="1">
 <path d="M0 120H1600M0 200H1600M0 280H1600M0 360H1600M0 440H1600M0 520H1600M0 600H1600M0 680H1600M0 760H1600M0 840H1600M0 920H1600"/>
 <path d="M80 0V1000M160 0V1000M240 0V1000M320 0V1000M400 0V1000M480 0V1000M560 0V1000M640 0V1000M720 0V1000M800 0V1000M880 0V1000M960 0V1000M1040 0V1000M1120 0V1000M1200 0V1000M1280 0V1000M1360 0V1000M1440 0V1000M1520 0V1000"/>
</g>
<g filter="url(#shadow)">
 <rect x="180" y="180" width="1240" height="620" rx="20" fill="#0c1418" stroke="#60716e" stroke-width="3"/>
 <rect x="208" y="210" width="1184" height="560" rx="9" fill="url(#screen)"/>
 <path d="M208 285H1392" stroke="#45575b" stroke-width="3"/>
 <circle cx="252" cy="245" r="9" fill="#ff5c2a"/><circle cx="285" cy="245" r="9" fill="#70837a"/><circle cx="318" cy="245" r="9" fill="#70837a"/>
</g>
<g font-family="DejaVu Sans,Arial,sans-serif">
 <text x="365" y="254" font-size="28" fill="#e8eee6" font-weight="700" letter-spacing="3">WEBSITE HEALTH MONITOR</text>
 <text x="255" y="340" font-size="19" fill="#a7b9b5" letter-spacing="4">MAINTENANCE STATUS</text>
 <text x="255" y="403" font-size="52" fill="#ff784c" font-weight="800">SITE CARE</text>
 <text x="255" y="454" font-size="22" fill="#c0cdc8">Updates • Backups • Uptime • SSL</text>
</g>
<g fill="#142126" stroke="#536865" stroke-width="2">
 <rect x="260" y="520" width="255" height="160" rx="10"/>
 <rect x="540" y="520" width="255" height="160" rx="10"/>
 <rect x="820" y="520" width="255" height="160" rx="10"/>
</g>
<g font-family="DejaVu Sans,Arial,sans-serif" font-weight="700">
 <text x="285" y="562" font-size="20" fill="#c0cbc6">BACKUP CHECK</text><text x="285" y="627" font-size="31" fill="#ff784c">READY</text>
 <text x="565" y="562" font-size="20" fill="#c0cbc6">SITE STATUS</text><text x="565" y="627" font-size="31" fill="#ff784c">ONLINE</text>
 <text x="845" y="562" font-size="20" fill="#c0cbc6">SSL CHECK</text><text x="845" y="627" font-size="31" fill="#ff784c">REVIEWED</text>
</g>
<g transform="translate(1090 350)">
 <circle cx="0" cy="0" r="145" fill="#18272a" stroke="#ff7948" stroke-opacity=".6" stroke-width="3"/>
 <path d="M0-95L85-65V15Q73 83 0 116Q-73 83 -85 15V-65Z" fill="#122327" stroke="#ff784c" stroke-width="10"/>
 <path d="M-43 3L-10 34L53-34" fill="none" stroke="#ff784c" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>
</g>
<path d="M1220 820V890M1190 890H1250M450 820V890M420 890H480" stroke="#42545a" stroke-width="15" stroke-linecap="round"/>
<g font-family="DejaVu Sans,Arial,sans-serif"><text x="800" y="940" text-anchor="middle" font-size="21" letter-spacing="9" fill="#abbdb6">PROACTIVE WEBSITE MAINTENANCE</text></g>
</svg>
'''


def replace_once(s: str, needle: str, new: str, label: str) -> str:
    n = s.count(needle)
    if n != 1:
        raise RuntimeError(f'{label}: expected 1 anchor, found {n}; no changes made.')
    return s.replace(needle, new, 1)


def collect(root: Path):
    files = {
        'service': root / 'app/marketing_services.py',
        'checkout': root / 'app/checkout.py',
        'home': root / 'app/templates/index.html',
        'overview': root / 'app/templates/marketing.html',
        'css': root / 'app/static/site.css',
    }
    image = root / 'app/static/images/website-maintenance.svg'
    for name, p in files.items():
        if not p.is_file():
            raise RuntimeError(f'Missing {p} ({name}); run from ~/reboot-syndicate.')
    src = {name: path.read_text(encoding='utf-8') for name, path in files.items()}
    flags = [
        'REBOOT_SERVICE_15_BEGIN' in src['service'],
        'REBOOT_SERVICE_15_CHECKOUT' in src['checkout'],
        'REBOOT_SERVICE_15_CARD' in src['home'],
        'REBOOT_SERVICE_15_OVERVIEW' in src['overview'],
        'REBOOT_SERVICE_15_STYLES' in src['css'],
        image.is_file(),
    ]
    if all(flags):
        return files, image, src, None
    if any(flags):
        raise RuntimeError('Partial Service #15 installation detected. No changes made; inspect backup and source files before retrying.')
    if any('website-maintenance' in s for s in src.values()):
        raise RuntimeError('Service slug already appears in source without expected installer marker; no changes made.')

    svc = src['service']
    svc = replace_once(svc, "@router.get('/marketing/{slug}')", SERVICE_BLOCK + "@router.get('/marketing/{slug}')", 'Service registry and SEO data')
    svc = replace_once(svc, '    image_version = sha256(image_path.read_bytes()).hexdigest()[:12] if image_path.is_file() else \'missing\'',
        '    if slug == "website-maintenance":\n        image_path = image_dir / "website-maintenance.svg"\n'
        "    image_version = sha256(image_path.read_bytes()).hexdigest()[:12] if image_path.is_file() else 'missing'", 'Artwork routing')

    checkout = replace_once(src['checkout'], 'def configured():', CHECKOUT_BLOCK + 'def configured():', 'Stripe service catalog')

    home = replace_once(src['home'],
        '<span class="agency-arrow">EXPLORE SERVICE ↗</span></a></div></section>',
        '<span class="agency-arrow">EXPLORE SERVICE ↗</span></a>' + CARD + '</div></section>',
        'Homepage services last card')
    home = replace_once(home,
        '<option value="Other / Not Sure Yet">Other / Not Sure Yet</option>',
        FORM_OPTION + '<option value="Other / Not Sure Yet">Other / Not Sure Yet</option>',
        'Consultation select control')

    overview = replace_once(src['overview'],
        '</p></a></section>\n<section id="packages"',
        '</p></a>' + OVERVIEW + '</section>\n<section id="packages"',
        'Marketing overview services ending')

    css = src['css'] + STYLE

    # Compile Python and parse Jinja before touching website files.
    compile(svc, str(files['service']), 'exec')
    compile(checkout, str(files['checkout']), 'exec')
    try:
        from jinja2 import Environment
        jinja = Environment()
        jinja.parse(home)
        jinja.parse(overview)
    except ImportError:
        print('Jinja2 unavailable on host; Docker will validate templates.')

    from xml.etree import ElementTree as ET
    ET.fromstring(IMAGE)

    # Validate exactly one link to new service in each overview and a matching form option.
    assert home.count('href="/marketing/website-maintenance"') == 1
    assert overview.count('href="/marketing/website-maintenance"') == 1
    assert home.count(FORM_OPTION) == 1
    planned = dict(src)
    planned.update(service=svc, checkout=checkout, home=home, overview=overview, css=css)
    return files, image, src, planned


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--check', action='store_true', help='only validate; do not edit site files (default)')
    group.add_argument('--apply', action='store_true', help='back up and apply Service #15 changes')
    args = parser.parse_args()
    root = Path.cwd()
    files, image, originals, planned = collect(root)
    if planned is None:
        print('ALREADY INSTALLED: all service #15 files and asset are present. Nothing changed.')
        return
    print('PASS: 15th service registry, $99/month server-side checkout entry, homepage tile, marketing overview, consultation option, SEO and illustration validated.')
    if not args.apply:
        print('DRY RUN PASSED: no files changed. Run --apply to install.')
        return
    backup = Path.home() / 'reboot-service15-backups' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    for name, path in files.items():
        dest = backup / path.relative_to(root)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
    print('BACKUP:', backup)
    changed = []
    try:
        for name, path in files.items():
            tmp = path.with_name(path.name + '.service15.tmp')
            tmp.write_text(planned[name], encoding='utf-8')
            tmp.chmod(path.stat().st_mode)
            tmp.replace(path)
            changed.append(name)
        image.write_text(IMAGE, encoding='utf-8')
        print('INSTALLED: Website Maintenance & Security (service #15).')
        print('Included: $99/month starter, service details, SEO, card, consultation option, checkout SKU, new SVG asset.')
        print('Sitemap adds the new service automatically because it reads SERVICES.')
        print('Next: docker compose config --quiet && docker compose up -d --build website')
    except Exception:
        for name in changed:
            files[name].write_text(originals[name], encoding='utf-8')
        if image.exists():
            image.unlink()
        raise
    finally:
        for p in files.values():
            tmp = p.with_name(p.name + '.service15.tmp')
            if tmp.exists():
                tmp.unlink()


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('ERROR:', exc, file=sys.stderr)
        sys.exit(1)
