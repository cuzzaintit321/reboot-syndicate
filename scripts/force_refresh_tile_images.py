#!/usr/bin/env python3
"""Install and display all 14 clearer Reboot Syndicate tile images.

Use from ~/reboot-syndicate after copying reboot-syndicate-14-clear-tiles.zip
to that directory. Does not use git pull; preserves Docker, logo, forms,
database, and other local customizations. Includes a CSS/image cache bust.
"""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = Path.cwd()
CSS = ROOT / "app/static/site.css"
HOME = ROOT / "app/templates/index.html"
IMAGES = ROOT / "app/static/images"
ZIP = ROOT / "reboot-syndicate-14-clear-tiles.zip"
STAGED = ROOT / "clear_tiles"

# First 16 SHA256 hex characters of each file in the delivered ZIP.
EXPECTED = {
    "website-design": "779ba32cb46a4d9b",
    "local-seo": "8ff2fe26bc9dce23",
    "google-business-profile": "3478532c291a51a5",
    "social-media": "9eb42b7bf121af99",
    "digital-advertising": "3f91c473a4059092",
    "lead-automation": "8fca3f521d0c310e",
    "branding-design": "2cdffd366645d4aa",
    "content-marketing": "21311cc011e027ba",
    "email-sms": "df0fae4b1486621d",
    "reputation-management": "e6fbfc0b427d9be4",
    "ecommerce": "da2b36f4044ed58e",
    "analytics-conversion": "d6cfc2e1bf7b6815",
    "business-technology": "4b25cd867bee5f64",
    "it-support": "276d49d44d985456",
}

if not (ROOT / "docker-compose.yml").is_file() or not CSS.is_file() or not HOME.is_file():
    sys.exit("ERROR: Run from ~/reboot-syndicate; expected site files are missing.")

# Validate the source of every image BEFORE overwriting anything.
archive = zipfile.ZipFile(ZIP) if ZIP.is_file() else None
sources = {}
missing = []
for slug, expected_hash in EXPECTED.items():
    filename = slug + ".webp"
    destination = IMAGES / filename
    staged = STAGED / filename
    candidates = []
    if staged.is_file():
        candidates.append(("clear_tiles", staged.read_bytes()))
    if archive and "clear_tiles/" + filename in archive.namelist():
        candidates.append(("ZIP", archive.read("clear_tiles/" + filename)))
    if destination.is_file():
        candidates.append(("already installed", destination.read_bytes()))
    choice = next(((origin, data) for origin, data in candidates
                   if sha256(data).hexdigest().startswith(expected_hash)
                   and data[:4] == b"RIFF" and data[8:12] == b"WEBP"), None)
    if choice is None:
        missing.append(filename)
    else:
        sources[slug] = choice
if archive:
    archive.close()
if missing:
    sys.exit(
        "ERROR: Cannot find the new images: " + ", ".join(missing) + "\n"
        "Copy reboot-syndicate-14-clear-tiles.zip from Fedora Downloads to "
        "~/reboot-syndicate/ on yeet, then rerun this installer."
    )

stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
BACKUP = ROOT / "backups" / ("clear-tile-repair-" + stamp)
def backup(path):
    if path.is_file():
        location = BACKUP / path.relative_to(ROOT)
        location.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, location)

IMAGES.mkdir(parents=True, exist_ok=True)
installed = 0
for slug, (origin, image_bytes) in sources.items():
    dest = IMAGES / (slug + ".webp")
    if dest.exists() and sha256(dest.read_bytes()).digest() == sha256(image_bytes).digest():
        print("Verified:", slug, "(already installed)")
        continue
    backup(dest)
    dest.write_bytes(image_bytes)
    installed += 1
    print("Replaced:", slug, "from", origin)
print(f"Verified {len(sources)} new images, replaced {installed} files.")

# Previous installer used a dark overlay and only 38% visibility before hover.
# Override it at the END of local CSS; keep all existing styles unchanged.
MARKER = "/* R/S clear 14 service tiles v3: visible photos and unique image URLs */"
css = CSS.read_text(encoding="utf-8")
overrides = [
    "",
    MARKER,
    ".agency-home .agency-service-card::before {",
    "  background-image:linear-gradient(180deg,rgba(7,11,13,.30) 0%,rgba(7,11,13,.38) 52%,rgba(7,11,13,.76) 100%),var(--card-photo)!important;",
    "  background-size:cover,cover!important;",
    "  background-position:center,center!important;",
    "  opacity:.92!important;",
    "  filter:saturate(1.12) contrast(1.07);",
    "}",
    ".agency-home .agency-service-card:hover::before,",
    ".agency-home .agency-service-card:focus-visible::before {",
    "  background-image:linear-gradient(180deg,rgba(7,11,13,.15) 0%,rgba(7,11,13,.32) 52%,rgba(7,11,13,.70) 100%),var(--card-photo)!important;",
    "  opacity:1!important;",
    "}",
    ".agency-home .agency-service-card > * {",
    "  text-shadow:0 1px 4px rgba(0,0,0,.75);",
    "}",
]
for slug, (_, image_bytes) in sources.items():
    version = sha256(image_bytes).hexdigest()[:12]
    overrides.append(
        '.agency-home .agency-service-card[href="/marketing/' + slug + '"]'
        '{--card-photo:url("/static/images/' + slug + '.webp?v=' + version + '")!important}'
    )
new_rules = "\n".join(overrides) + "\n"
if MARKER in css:
    # Only replace our own marked section; preserve any CSS written afterwards.
    start = css.index(MARKER)
    next_section = css.find("\n/* ", start + len(MARKER))
    if next_section == -1:
        next_section = len(css)
    css_new = css[:start] + new_rules.lstrip("\n") + css[next_section:]
else:
    css_new = css.rstrip() + "\n\n" + new_rules
if css_new != css:
    backup(CSS)
    CSS.write_text(css_new, encoding="utf-8")
    print("Updated CSS: much clearer images at rest and on hover.")

# Changing the CSS URL bypasses stale browser/CDN caches of /static/site.css.
page = HOME.read_text(encoding="utf-8")
css_version = sha256(css_new.encode("utf-8")).hexdigest()[:12]
page_new, count = re.subn(
    r'href="/static/site\.css(?:\?[^"]*)?"',
    'href="/static/site.css?v=tiles-' + css_version + '"',
    page, count=1
)
if count != 1:
    sys.exit("ERROR: Homepage stylesheet link missing; images installed, but cache bust not applied.")
if page != page_new:
    backup(HOME)
    HOME.write_text(page_new, encoding="utf-8")
    print("Updated homepage CSS link to force fresh assets.")

print("Backup:", BACKUP if BACKUP.is_dir() else "not needed")
print("Rebuilding website (only) with Docker Compose...")
subprocess.run(["docker", "compose", "up", "-d", "--build", "website"], check=True)
print("\nCOMPLETE: 14 images verified, more visible, and cache-busted.")
print("Open https://rebootsyndicate.com/ and press Ctrl+Shift+R.")
