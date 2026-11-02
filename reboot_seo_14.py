#!/usr/bin/env python3
"""Reboot Syndicate SEO phase 1: 14 unique, useful, locally relevant service pages.

Run from ~/reboot-syndicate. Default is a no-write audit; use --apply to install.
The script deliberately does NOT change checkout, emails, database, DNS, or routes.
"""
from __future__ import annotations

import argparse
import datetime as dt
import pprint
import shutil
from pathlib import Path

# Titles/descriptions are editorial, not ranking guarantees. The visible copy
# reflects the offerings already documented in app/marketing_services.py.
LOCAL_SEO = {
    "website-design": {
        "title": "Web Design in Titusville & Brevard County | Reboot Syndicate",
        "description": "Website design and redesign for Titusville, Mims and Brevard County businesses. Responsive pages, landing pages and clear customer contact paths.",
        "heading": "WEBSITE DESIGN", "emphasis": "FOR REAL BUSINESSES.",
        "copy": "Need a business website in Titusville, Mims or elsewhere in Brevard County? We help plan responsive websites, useful service pages, focused landing pages and straightforward quote or contact forms. Remote website projects are also available.",
        "related": ["local-seo", "google-business-profile", "ecommerce"],
    },
    "local-seo": {
        "title": "Local SEO Services in Titusville, FL | Reboot Syndicate",
        "description": "Local SEO for Titusville and Brevard County businesses: page titles, useful service content, internal links, technical checks and local search strategy.",
        "heading": "LOCAL SEO", "emphasis": "THAT MAKES SENSE.",
        "copy": "For Titusville and Brevard County businesses, local SEO starts with searchable service information, clear site structure and accurate business details. We review indexing, page relevance, technical issues and practical opportunities for improving search visibility without promising rankings.",
        "related": ["website-design", "google-business-profile", "content-marketing"],
    },
    "google-business-profile": {
        "title": "Google Business Profile Help | Titusville FL | Reboot Syndicate",
        "description": "Google Business Profile setup and optimization help for eligible Titusville and Brevard County businesses. Categories, services, photos and listing accuracy.",
        "heading": "GOOGLE BUSINESS", "emphasis": "PROFILE SUPPORT.",
        "copy": "We help eligible businesses in Titusville, Mims and the surrounding Brevard County area review Google Business Profile categories, service information, contact details, photos and customer review responses. The owner keeps control of the profile, and Google makes verification decisions.",
        "related": ["local-seo", "reputation-management", "website-design"],
    },
    "social-media": {
        "title": "Social Media Management | Titusville FL | Reboot Syndicate",
        "description": "Social media content planning and branded graphics for Titusville and Brevard County small businesses. Consistent posts, captions and publishing plans.",
        "heading": "SOCIAL MEDIA", "emphasis": "WITH PURPOSE.",
        "copy": "Titusville and Brevard County small businesses need social content that clearly reflects their brand. We plan campaign themes, create graphics and captions, organize content calendars and help with approved publishing and performance reviews.",
        "related": ["content-marketing", "branding-design", "digital-advertising"],
    },
    "digital-advertising": {
        "title": "Google Ads & Meta Ads Management | Titusville FL",
        "description": "Google Ads and Meta ad campaign planning for Titusville and Brevard County businesses. Strategy, creative, landing pages and conversion tracking.",
        "heading": "PAID ADS", "emphasis": "WITH CLEAR GOALS.",
        "copy": "For Brevard County businesses exploring Google Ads, Facebook or Instagram advertising, we help define a campaign objective, audience, offer and landing page. Advertising budgets and management fees are agreed separately, and performance is measured rather than guaranteed.",
        "related": ["website-design", "analytics-conversion", "social-media"],
    },
    "lead-automation": {
        "title": "Lead Automation & CRM Workflows | Reboot Syndicate",
        "description": "Lead capture, CRM workflows, follow-up reminders and practical AI-assisted marketing automation for small businesses in Brevard County and remotely.",
        "heading": "LEAD AUTOMATION", "emphasis": "THAT FOLLOWS THROUGH.",
        "copy": "Small businesses often receive inquiries through websites, calls and different apps. We build practical lead-capture forms, CRM handoffs, notifications and approved follow-up workflows for businesses in Brevard County and remote teams, with clear oversight and testing.",
        "related": ["email-sms", "business-technology", "analytics-conversion"],
    },
    "branding-design": {
        "title": "Logo & Branding Design in Titusville FL | Reboot Syndicate",
        "description": "Logo concepts, brand identity and graphic design for Titusville and Brevard County businesses. Visual systems, social graphics and marketing assets.",
        "heading": "BRANDING & LOGOS", "emphasis": "BUILT TO FIT.",
        "copy": "From new Titusville businesses to established Brevard County brands, we can help create an organized visual identity with logos, color palettes, typography and useful graphics for websites, social posts, promotions and print materials.",
        "related": ["website-design", "social-media", "content-marketing"],
    },
    "content-marketing": {
        "title": "Website Copywriting & Content Marketing | Brevard County",
        "description": "Website copywriting, service page content, articles and campaign messaging for Titusville and Brevard County businesses, with remote projects available.",
        "heading": "CONTENT & COPY", "emphasis": "THAT EXPLAINS VALUE.",
        "copy": "We help Titusville and Brevard County businesses explain their services clearly through original website copy, service pages, articles, customer-focused messages and content plans. The aim is useful writing that fits your voice and answers real customer questions.",
        "related": ["local-seo", "website-design", "social-media"],
    },
    "email-sms": {
        "title": "Email & SMS Marketing Services | Reboot Syndicate",
        "description": "Permission-based email and SMS marketing for small businesses: newsletters, subscriber journeys, follow-ups and opt-out-conscious campaign planning.",
        "heading": "EMAIL & SMS", "emphasis": "WITH PERMISSION.",
        "copy": "Businesses in Brevard County and beyond can use permission-based newsletters, appointment reminders and customer follow-ups to stay in touch. We help organize opted-in audiences, messaging, sending workflows and unsubscribe or opt-out checks.",
        "related": ["lead-automation", "content-marketing", "analytics-conversion"],
    },
    "reputation-management": {
        "title": "Online Review & Reputation Management | Titusville FL",
        "description": "Review monitoring, ethical customer review requests and response assistance for Titusville and Brevard County small businesses.",
        "heading": "ONLINE REVIEWS", "emphasis": "HANDLED WELL.",
        "copy": "For local businesses in Titusville and Brevard County, real customer reviews and thoughtful responses help visitors understand the experience you provide. We help organize honest review requests, review monitoring and professional response workflows—never fabricated reviews.",
        "related": ["google-business-profile", "local-seo", "social-media"],
    },
    "ecommerce": {
        "title": "E-Commerce Website Design | Titusville FL | Reboot Syndicate",
        "description": "E-commerce website design for Titusville and Brevard County small businesses: product catalogs, online store setup, checkout integration and mobile shopping.",
        "heading": "E-COMMERCE", "emphasis": "THAT'S EASY TO USE.",
        "copy": "We help small brands in Titusville, Mims and across Brevard County set up or improve online stores. That can include product and category pages, navigation, product listings, responsive shopping experiences and supported payment integrations.",
        "related": ["website-design", "analytics-conversion", "digital-advertising"],
    },
    "analytics-conversion": {
        "title": "Website Analytics & Conversion Tracking | Brevard County",
        "description": "Analytics setup, website conversion tracking and practical reporting for Brevard County businesses. Understand forms, calls, campaigns and page performance.",
        "heading": "ANALYTICS", "emphasis": "YOU CAN ACT ON.",
        "copy": "Businesses in Brevard County and beyond can use website analytics to understand how people reach important pages and whether they call, submit forms or take other useful actions. We help plan measurement, configure supported tools and review opportunities to improve visitor experience.",
        "related": ["digital-advertising", "website-design", "local-seo"],
    },
    "business-technology": {
        "title": "Small Business Technology Setup | Titusville FL",
        "description": "Small business technology help in Titusville and Brevard County: business email, domains, DNS, hosting, SSL, backups and connected software.",
        "heading": "BUSINESS TECH", "emphasis": "THAT STAYS CONNECTED.",
        "copy": "Behind a working business website are domains, DNS, hosting, SSL certificates, professional email and connected software. We help Titusville and Brevard County businesses plan, configure and troubleshoot these essential systems with clear ownership and handoff.",
        "related": ["website-design", "it-support", "lead-automation"],
    },
    "it-support": {
        "title": "Computer Repair & IT Support in Titusville FL | Reboot Syndicate",
        "description": "Computer troubleshooting, Wi-Fi networking, backups and small-business IT support for Titusville, Mims and nearby Brevard County customers; availability confirmed.",
        "heading": "COMPUTER REPAIR", "emphasis": "& LOCAL IT HELP.",
        "copy": "Reboot Syndicate provides practical IT help for Titusville, Mims and nearby Brevard County customers, subject to availability. We review computer and laptop issues, Wi-Fi problems, backups, upgrades and common office technology needs before agreeing on a scope.",
        "related": ["business-technology", "website-design", "lead-automation"],
    },
}

# Existing patterns from current Reboot Syndicate repository. We require them
# rather than guessing if the local code has changed significantly.
TITLE_OLD = '<title>Reboot Syndicate | {{ seo_title | replace(\' | Reboot Syndicate\', \'\') }}</title>'
TITLE_NEW = '<title>{{ seo_title }}</title>'
HEADING_OLD = '<h2>MORE THAN<br><em>A QUICK FIX.</em></h2>'
HEADING_NEW = '<h2>{{ seo_topic_heading }}<br><em>{{ seo_topic_emphasis }}</em></h2>'
COPY_OLD = "<p>Every project is scoped to your needs. Here's the type of work we can include for {{ service.name|lower }}.</p>"
COPY_NEW = '<p>{{ seo_local_copy }}</p>'
VIEW_CTX = "        'seo_description': SEO_METADATA[slug]['description'],"
SERVICE_ROUTER = "@router.get('/marketing/{slug}')"
RELATED_SECTION_MARK = '<section class="agency-detail-cta section-wrap">'
SEO_MARKER = '# REBOOT_SEO_14_START'
CSS_MARKER = '/* REBOOT_SEO_14_START */'

RELATED_SECTION = '''<!-- REBOOT_SEO_14_START -->
<section class="agency-detail-section section-wrap rs-related-section" aria-labelledby="related-services-title">
  <span class="section-index">RELATED SERVICES / REBOOT SYNDICATE</span>
  <h2 id="related-services-title">SERVICES THAT<br><em>WORK TOGETHER.</em></h2>
  <p>Explore related services for your next project, or get in touch to discuss the right starting point.</p>
  <nav class="rs-related-links" aria-label="Related marketing and business services">
    {% for related_slug, related_name in related_services %}
    <a href="/marketing/{{ related_slug }}">{{ related_name }} <span aria-hidden="true">↗</span></a>
    {% endfor %}
  </nav>
</section>
'''

BREADCRUMB_JSONLD = '''<!-- REBOOT_SEO_14_BREADCRUMBS -->
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
{"@type":"ListItem","position":1,"name":"Home","item":"https://rebootsyndicate.com/"},
{"@type":"ListItem","position":2,"name":"Services","item":"https://rebootsyndicate.com/marketing"},
{"@type":"ListItem","position":3,"name":{{ service.name|tojson }},"item":{{ canonical_url|tojson }}}
]}
</script>
'''

CSS_EXTRA = '''\n/* REBOOT_SEO_14_START */
.rs-related-section {background:#121b1e;border-top:1px solid #3c4a4c}
.rs-related-section > p {max-width:680px;color:#bdcac2;line-height:1.7;margin:20px 0 28px}
.rs-related-links {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.rs-related-links a {display:flex;align-items:center;justify-content:space-between;gap:14px;min-height:88px;padding:20px;border:1px solid #526063;background:#1b2528;color:#f4f1e8;font:800 17px/1.2 'Barlow Condensed',Impact,sans-serif;text-transform:uppercase}
.rs-related-links a span {color:var(--accent)}
.rs-related-links a:hover,.rs-related-links a:focus-visible {border-color:var(--accent);background:#263236}
@media(max-width:800px){.rs-related-links {grid-template-columns:1fr 1fr}}
@media(max-width:520px){.rs-related-links {grid-template-columns:1fr}.rs-related-links a{min-height:62px}}
/* REBOOT_SEO_14_END */
'''


def exactly_one(source: str, old: str, new: str, description: str) -> str:
    n = source.count(old)
    if n != 1:
        raise RuntimeError(f"{description}: expected one anchor, found {n}. No files changed.")
    return source.replace(old, new, 1)


def stage_changes(root: Path):
    service_path = root / 'app/marketing_services.py'
    template_path = root / 'app/templates/marketing_detail.html'
    css_path = root / 'app/static/site.css'
    for p in (service_path, template_path, css_path):
        if not p.is_file():
            raise RuntimeError(f"Missing {p}. Run from ~/reboot-syndicate on yeet.")
    original = {p: p.read_text() for p in (service_path, template_path, css_path)}
    service, tpl, css = (original[p] for p in (service_path, template_path, css_path))

    # Verify registry really has the 14 slugs, and the update isn't repeated.
    markers = (SEO_MARKER in service, '<!-- REBOOT_SEO_14_START -->' in tpl, CSS_MARKER in css)
    if all(markers):
        return original, None
    if any(markers):
        raise RuntimeError('Partial SEO phase 1 markers found. No modifications made; inspect files before retrying.')
    if 'SEO_METADATA = {' not in service or SERVICE_ROUTER not in service:
        raise RuntimeError('Expected service registry/route is missing. No files changed.')
    for slug in LOCAL_SEO:
        if f'"{slug}":' not in service:
            raise RuntimeError(f"Service {slug} missing from module. No files changed.")
    if TITLE_NEW in tpl:
        # Already improved title tag; accept rather than overriding it.
        pass
    else:
        tpl = exactly_one(tpl, TITLE_OLD, TITLE_NEW, 'Page title template')
    tpl = exactly_one(tpl, HEADING_OLD, HEADING_NEW, 'Unique H2 template')
    tpl = exactly_one(tpl, COPY_OLD, COPY_NEW, 'Local service paragraph template')
    tpl = exactly_one(tpl, RELATED_SECTION_MARK, RELATED_SECTION + RELATED_SECTION_MARK, 'Related links insertion')
    tpl = exactly_one(tpl, '</head>', BREADCRUMB_JSONLD + '</head>', 'Breadcrumbs insertion')

    serialized = pprint.pformat(LOCAL_SEO, width=100, sort_dicts=False)
    extra = f'''{SEO_MARKER}
LOCAL_SEO = {serialized}
for _slug, _seo in LOCAL_SEO.items():
    SEO_METADATA[_slug].update(title=_seo['title'], description=_seo['description'])
# REBOOT_SEO_14_END

'''
    service = exactly_one(service, SERVICE_ROUTER, extra + SERVICE_ROUTER, 'SEO metadata insertion')
    ctx = "        'seo_topic_heading': LOCAL_SEO[slug]['heading'],\n" \
          "        'seo_topic_emphasis': LOCAL_SEO[slug]['emphasis'],\n" \
          "        'seo_local_copy': LOCAL_SEO[slug]['copy'],\n" \
          "        'related_services': [(s, SERVICES[s]['name']) for s in LOCAL_SEO[slug]['related']],\n"
    service = exactly_one(service, VIEW_CTX, VIEW_CTX + '\n' + ctx.rstrip('\n'), 'SEO context insertion')

    # Check Python and Jinja syntax before changing anything.
    compile(service, str(service_path), 'exec')
    try:
        from jinja2 import Environment
        Environment().parse(tpl)
    except ImportError:
        print('Jinja2 not installed locally; skipping template parser validation.')
    updated = {service_path: service, template_path: tpl, css_path: css + CSS_EXTRA}
    return original, updated


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='back up files, then install SEO phase 1')
    parser.add_argument('--check', action='store_true', help='validate without modifying files (default)')
    args = parser.parse_args()
    root = Path.cwd()
    original, updated = stage_changes(root)
    if updated is None:
        print('SEO phase 1 is already installed in all 3 files. No changes needed.')
        return
    print(f'Validated all {len(LOCAL_SEO)} service slugs and templates.')
    print('Changes: 14 titles/descriptions, unique service H2s and local copy, related links, breadcrumb JSON-LD, small related-links styles.')
    if not args.apply:
        print('DRY RUN PASSED. No files changed. Run with --apply to install.')
        return
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backdir = Path.home() / 'reboot-seo-backups' / stamp
    for p in original:
        dest = backdir / p.relative_to(root)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
    print(f'Backups saved outside the site at: {backdir}')
    try:
        for p, content in updated.items():
            p.write_text(content)
    except Exception:
        for p, content in original.items():
            p.write_text(content)
        raise
    print('INSTALLED: SEO phase 1. Desktop and mobile styles, payments, emails and DB were not modified except for new related-link styling.')
    print('Next: docker compose up -d --build website, then validate the page output and sitemap.')


if __name__ == '__main__':
    main()
