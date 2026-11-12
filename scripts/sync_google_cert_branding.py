#!/usr/bin/env python3
"""Apply only the Google branding correction to the live Reboot Syndicate checkout.

The rest of the customized homepage, CSS, and other issuer logos are preserved.
Backups of changed files are saved in /tmp before writing.
"""
from pathlib import Path
from urllib.request import Request, urlopen
import re
import shutil
import sys
import tempfile

ROOT = Path.cwd()
HOME = ROOT / "app/templates/index.html"
LOGO = ROOT / "app/static/brands/google.svg"
SOURCE = "https://raw.githubusercontent.com/cuzzaintit321/reboot-syndicate/main/app/static/brands/google.svg"
VERSION = "single-g-20261102"

def download_logo():
    req = Request(SOURCE, headers={"User-Agent": "RebootSyndicateBrandSync/1.0"})
    with urlopen(req, timeout=25) as response:
        data = response.read().decode("utf-8")
    if not data.lstrip().startswith("<svg") or any(color not in data for color in
        ("#e33629", "#f8bd00", "#587dbd", "#319f43")):
        raise ValueError("Downloaded Google icon is not the expected multicolor SVG.")
    return data

def main():
    if not HOME.is_file():
        raise FileNotFoundError("Run from ~/reboot-syndicate: app/templates/index.html was not found.")
    markup = HOME.read_text(encoding="utf-8")
    about_pattern = re.compile(r'<section\b[^>]*\bid="about"[^>]*>[\s\S]*?</section>', re.I)
    abouts = list(about_pattern.finditer(markup))
    if len(abouts) != 1:
        raise ValueError("Could not locate exactly one About section. No changes applied.")
    about = abouts[0].group()
    old = "<small>Google Digital Academy</small>"
    new = "<small>Google</small>"
    count = about.count(old)
    if count not in (0, 2):
        raise ValueError(f"Expected zero or two old Google issuer labels; found {count}. No changes applied.")
    if about.count('src="/static/brands/google.svg') != 2:
        raise ValueError("Expected exactly two Google logo images. No changes applied.")
    about = about.replace(old, new)
    about = re.sub(
        r'src="/static/brands/google\.svg(?:\?[^"]*)?"',
        f'src="/static/brands/google.svg?v={VERSION}"',
        about,
    )
    # The SVG has transparent regions. Hide the fallback G so it doesn't show
    # through the icon. If the image fails, onerror reveals the backup letter.
    logo_prefix = '<span class="rs-about-issuer-mark rs-about-mark-google">'
    img_prefix = f'<img src="/static/brands/google.svg?v={VERSION}" alt="" width="24" height="24" loading="lazy"'
    old_logo = logo_prefix + '<span aria-hidden="true">G</span>' + img_prefix + ' onerror="this.style.display=\'none\'"></span>'
    fixed_logo = logo_prefix + '<span aria-hidden="true" hidden>G</span>' + img_prefix + ' onerror="this.style.display=\'none\';this.previousElementSibling.hidden=false"></span>'
    old_logo_count = about.count(old_logo)
    if old_logo_count not in (0, 2):
        raise ValueError(f"Unexpected Google fallback markup ({old_logo_count}). No changes applied.")
    about = about.replace(old_logo, fixed_logo)
    if about.count(fixed_logo) != 2:
        raise ValueError("Expected two fixed Google marks; no changes applied.")
    if about.count(new) != 2 or about.count(f"google.svg?v={VERSION}") != 2:
        raise ValueError("Google certificate validation failed. No changes applied.")
    updated = markup[:abouts[0].start()] + about + markup[abouts[0].end():]
    google_icon = download_logo()
    modifications = {}
    if markup != updated:
        modifications[HOME] = updated
    if not LOGO.exists() or LOGO.read_text(encoding="utf-8") != google_icon:
        modifications[LOGO] = google_icon
    if not modifications:
        print("Google certificate branding already up to date.")
        return
    backup = Path(tempfile.mkdtemp(prefix="rs-google-branding-", dir="/tmp"))
    for file in modifications:
        if file.exists():
            target = backup / file.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, target)
    for file, content in modifications.items():
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content, encoding="utf-8")
        print("Updated:", file.relative_to(ROOT))
    print("Backups:", backup)
    print("Google issuer labels: 2 updated/verified; full-color G icons: 2 linked.")
    print("Rebuild with: docker compose up -d --build website")

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("ERROR:", error, file=sys.stderr)
        raise SystemExit(1)
