#!/usr/bin/env python3
"""Preview or install the regional SEO update from ~/reboot-syndicate on yeet."""

import argparse
import ast
from datetime import datetime, timezone
import fcntl
from html import escape
from itertools import accumulate
from pathlib import Path
import re
import shutil
import subprocess


PAGES = {
    "index.html": (
        "/",
        "Space Coast Web Design & Digital Marketing | Reboot Syndicate",
        "Web design, local SEO and digital marketing for businesses across Florida's Space Coast. Serving Brevard County and working with clients remotely.",
    ),
    "marketing.html": (
        "/marketing",
        "Space Coast Digital Marketing Services | Reboot Syndicate",
        "Explore web design, local SEO, social media, advertising and automation for Brevard County businesses and remote clients.",
    ),
    "brevard_county.html": (
        "/brevard-county",
        "Brevard County Web Design, SEO & Marketing | Reboot Syndicate",
        "Web design, local SEO, Google Business Profile help and digital marketing for Brevard County businesses across Florida's Space Coast.",
    ),
}

SERVICES = {
    "website-design": (
        "Space Coast Web Design | Reboot Syndicate",
        "Responsive website design, redesigns and landing pages for Brevard County businesses. Give customers a clear way to contact you or request a quote.",
    ),
    "local-seo": (
        "Space Coast Local SEO Services | Reboot Syndicate",
        "Help customers find your Brevard County business with local SEO, technical checks, useful service pages and clearer internal links.",
    ),
    "google-business-profile": (
        "Google Business Profile Help | Space Coast",
        "Google Business Profile setup and optimization for eligible Brevard County businesses. Get help with categories, services, photos and listing accuracy.",
    ),
    "social-media": (
        "Space Coast Social Media Management | Reboot Syndicate",
        "Social media planning, branded graphics, captions and publishing calendars for small businesses across Brevard County.",
    ),
    "digital-advertising": (
        "Google & Meta Ads Management | Space Coast",
        "Google Ads and Meta ad campaign planning for Brevard County businesses, including creative, landing pages and conversion tracking.",
    ),
    "branding-design": (
        "Space Coast Logo & Branding Design | Reboot Syndicate",
        "Logo concepts, visual identities and branded graphics for Brevard County businesses launching or updating their brands.",
    ),
    "content-marketing": (
        "Website Copywriting & Content Marketing | Brevard County",
        "Website copy, service pages, articles and campaign messaging for Space Coast businesses and remote clients.",
    ),
    "reputation-management": (
        "Review & Reputation Management | Space Coast",
        "Review monitoring, ethical review requests and response assistance for small businesses across Brevard County.",
    ),
    "ecommerce": (
        "Space Coast E-Commerce Web Design | Reboot Syndicate",
        "E-commerce website design for Brevard County businesses, including product catalogs, checkout integration and mobile shopping.",
    ),
    "business-technology": (
        "Small Business Technology Setup | Brevard County",
        "Business email, domains, DNS, hosting, SSL, backups and software setup for small businesses across Florida's Space Coast.",
    ),
    "it-support": (
        "Computer Repair & IT Support | Space Coast",
        "Computer troubleshooting, Wi-Fi, backups and small-business IT support in Brevard County. On-site availability is confirmed when you contact us.",
    ),
}

CITY_COPY = {
    "Need a business website in Titusville, Mims or elsewhere in Brevard County?": "Need a business website on the Space Coast?",
    "For Titusville and Brevard County businesses, local SEO": "For Brevard County businesses, local SEO",
    "eligible businesses in Titusville, Mims and the surrounding Brevard County area": "eligible businesses across Brevard County",
    "Titusville and Brevard County small businesses need": "Space Coast small businesses need",
    "From new Titusville businesses to established Brevard County brands": "From new businesses to established brands across the Space Coast",
    "help Titusville and Brevard County businesses": "help Brevard County businesses",
    "For local businesses in Titusville and Brevard County,": "For local businesses across the Space Coast,",
    "small brands in Titusville, Mims and across Brevard County": "small brands across the Space Coast",
    "for Titusville, Mims and nearby Brevard County customers": "for Brevard County customers",
    "Titusville and nearby customers": "Customers in Brevard County",
}

COVERAGE = """<!-- RS SPACE COAST COVERAGE START -->
<h3>North Brevard</h3>
<p>For service businesses in Mims, Titusville and Port St. John, we build <a href="/marketing/website-design">websites</a> that show where you work and give customers a clear way to request a quote.</p>
<h3>Central Brevard</h3>
<p>In Cocoa, Rockledge, Viera and Merritt Island, our <a href="/marketing/local-seo">local SEO</a> helps customers find your services, hours and contact information. Eligible businesses can also get <a href="/marketing/google-business-profile">Google Business Profile support</a>.</p>
<h3>South Brevard</h3>
<p>If you serve Palm Shores, Melbourne, Palm Bay, Malabar or Grant-Valkaria, we can connect your website inquiries to <a href="/marketing/lead-automation">lead follow-up workflows</a> that organize requests by location or service.</p>
<h3>Beachside</h3>
<p>For businesses in Cape Canaveral, Cocoa Beach, Satellite Beach, Indian Harbour Beach, Indialantic and Melbourne Beach, we can help visitors and residents find hours, book a service or buy online with <a href="/marketing/website-design">website design</a> and <a href="/marketing/ecommerce">e-commerce setup</a>.</p>
<!-- RS SPACE COAST COVERAGE END -->"""

TOWNS = (
    "Mims", "Cocoa", "Viera", "Palm Bay", "Melbourne", "Rockledge", "Titusville",
    "Palm Shores", "Malabar", "Grant-Valkaria", "Merritt Island", "Satellite Beach",
    "Cocoa Beach", "Indialantic", "Port St. John", "Cape Canaveral", "Melbourne Beach",
    "Indian Harbour Beach",
)


def replace_one(source, pattern, replacement):
    updated, count = re.subn(pattern, lambda match: replacement, source, flags=re.S)
    if count != 1:
        raise ValueError(f"Expected one match for {pattern!r}, found {count}.")
    return updated


def update_head(source, title, description=None):
    source = replace_one(source, r"<title>.*?</title>", f"<title>{title}</title>")
    source = replace_one(
        source, r'<meta property="og:title" content="[^"]*">',
        f'<meta property="og:title" content="{title}">',
    )
    if description is not None:
        for attribute in ('name="description"', 'property="og:description"'):
            source = replace_one(
                source, rf'<meta {attribute} content="[^"]*">',
                f'<meta {attribute} content="{description}">',
            )
    return source


def update_city_copy(source):
    for previous, regional in CITY_COPY.items():
        source = source.replace(previous, regional)
    return source


def update_registry(source):
    # Edit individual string literals so live service entries and local edits are retained.
    tree = ast.parse(source)
    registries = [
        node.value for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "SEO_METADATA" for target in node.targets)
    ]
    if len(registries) != 1 or not isinstance(registries[0], ast.Dict):
        raise ValueError("Expected one SEO_METADATA dictionary in app/marketing_services.py.")
    registry = registries[0]
    entries = dict(zip(map(ast.literal_eval, registry.keys), registry.values))
    raw = source.encode("utf-8")
    offsets = [0, *accumulate(map(len, raw.splitlines(keepends=True)))]
    edits = []
    for slug, (title, description) in SERVICES.items():
        entry = entries.get(slug)
        if not isinstance(entry, ast.Dict):
            raise ValueError(f"Missing SEO metadata for {slug}.")
        fields = dict(zip(map(ast.literal_eval, entry.keys), entry.values))
        for field, value in (("title", title), ("description", description)):
            node = fields.get(field)
            if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
                raise ValueError(f"Missing SEO {field} for {slug}.")
            if node.value != value:
                start = offsets[node.lineno - 1] + node.col_offset
                end = offsets[node.end_lineno - 1] + node.end_col_offset
                edits.append((start, end, ('"' + value + '"').encode("utf-8")))
    for start, end, value in sorted(edits, reverse=True):
        raw = raw[:start] + value + raw[end:]
    updated = update_city_copy(raw.decode("utf-8"))
    compile(updated, "app/marketing_services.py", "exec")
    return updated


def plan_updates():
    templates = Path("app/templates")
    updates = {}
    for name, (_, title, description) in PAGES.items():
        path = templates / name
        before = path.read_text(encoding="utf-8")
        after = update_head(before, escape(title), escape(description))
        if name == "brevard_county.html":
            if "<!-- RS SPACE COAST COVERAGE START -->" in after:
                pattern = r"<!-- RS SPACE COAST COVERAGE START -->.*?<!-- RS SPACE COAST COVERAGE END -->"
            else:
                pattern = r"<p>From Titusville and Mims in the north to Cocoa,[^<]*</p>"
            after = replace_one(after, pattern, COVERAGE)
        elif name == "marketing.html":
            after = after.replace(
                "helps small businesses build their online presence",
                "helps small businesses across the Space Coast build their online presence",
            )
        updates[path] = (before, after)
    path = templates / "marketing_detail.html"
    before = path.read_text(encoding="utf-8")
    updates[path] = (before, update_city_copy(update_head(before, "{{ seo_title }}")))
    path = Path("app/marketing_services.py")
    before = path.read_text(encoding="utf-8")
    updates[path] = (before, update_registry(before))
    return {path: (before, after) for path, (before, after) in updates.items() if before != after}


def verify_website():
    expected = list(PAGES.values()) + [
        (f"/marketing/{slug}", title, description) for slug, (title, description) in SERVICES.items()
    ]
    check = """
from html import unescape
import re
from urllib.request import urlopen

for path, title, description in EXPECTED:
    with urlopen('http://127.0.0.1:8000' + path, timeout=5) as response:
        markup = response.read().decode('utf-8')
    assert unescape(re.search(r'<title>(.*?)</title>', markup).group(1)) == title, path
    assert unescape(re.search(r'<meta name="description" content="([^"]*)"', markup).group(1)) == description, path
    assert unescape(re.search(r'<meta property="og:title" content="([^"]*)"', markup).group(1)) == title, path
    assert unescape(re.search(r'<meta property="og:description" content="([^"]*)"', markup).group(1)) == description, path
    assert f'<link rel="canonical" href="https://rebootsyndicate.com{path}">' in markup, path
    if path == '/brevard-county':
        assert COVERAGE in markup, 'Incomplete service-area coverage'
    if path.startswith('/marketing/'):
        assert 'titusville' not in markup.casefold(), path
print(f'Verified {len(EXPECTED)} updated pages and {TOWN_COUNT} communities.')
"""
    script = f"EXPECTED = {expected!r}\nCOVERAGE = {COVERAGE!r}\nTOWN_COUNT = {len(TOWNS)}\n" + check
    subprocess.run(["docker", "compose", "exec", "-T", "website", "python", "-c", script], check=True)


def deploy(updates):
    build = ["docker", "compose", "up", "-d", "--build", "--wait", "--wait-timeout", "90", "website"]
    if not updates:
        subprocess.run(build, check=True)
        verify_website()
        return
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    backup = Path("backups") / f"space-coast-seo-{stamp}"
    for path, (before, _) in updates.items():
        if path.read_text(encoding="utf-8") != before:
            raise SystemExit(f"{path} changed during preview. Run again.")
        target = backup / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    try:
        for path, (_, after) in updates.items():
            path.write_text(after, encoding="utf-8")
        subprocess.run(build, check=True)
        verify_website()
    except (Exception, KeyboardInterrupt):
        for path in updates:
            shutil.copy2(backup / path, path)
        subprocess.run(build, check=False)
        raise
    print(f"Original files backed up in {backup}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Back up files, apply edits and rebuild website")
    args = parser.parse_args()
    compose = Path("docker-compose.yml")
    if not compose.is_file():
        parser.error("Run this from ~/reboot-syndicate.")
    with compose.open() as lock:
        fcntl.flock(lock, fcntl.LOCK_EX if args.apply else fcntl.LOCK_SH)
        try:
            updates = plan_updates()
        except (OSError, ValueError, SyntaxError) as error:
            parser.error(str(error))
        print(f"Regional SEO for {len(PAGES) + len(SERVICES)} pages and {len(TOWNS)} communities.", flush=True)
        for path in updates:
            print(f"  {path}", flush=True)
        if args.apply:
            deploy(updates)
        else:
            print("Preview complete. Run again with --apply to deploy.")


if __name__ == "__main__":
    main()
