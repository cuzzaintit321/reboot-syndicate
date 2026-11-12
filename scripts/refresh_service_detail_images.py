#!/usr/bin/env python3
"""Fix blurry/cached images on all 14 Reboot Syndicate service detail pages.

Run on yeet from ~/reboot-syndicate:
    git fetch origin main
    git show origin/main:scripts/refresh_service_detail_images.py > /tmp/refresh_service_detail_images.py
    python3 /tmp/refresh_service_detail_images.py

It checks the new 1440x900 service image collection, restores outdated WebPs
from the existing 14-image ZIP or clear_tiles directory when needed, versions
each detail image URL by its content hash, and rebuilds only the website.
It will not change the homepage tiles, your logo, Docker configuration,
.env, customer records, pricing or other sites. Backs up anything it edits.
"""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import ast
import shutil
import subprocess
import sys
import zipfile

ROOT = Path.cwd()
SRC = ROOT / "app/marketing_services.py"
PAGE = ROOT / "app/templates/marketing_detail.html"
STATIC = ROOT / "app/static/images"
ARCHIVE = ROOT / "reboot-syndicate-14-clear-tiles.zip"
STAGED = ROOT / "clear_tiles"

# Hashes of the approved full-resolution images in the previously supplied ZIP.
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

if not (ROOT / "docker-compose.yml").is_file() or not SRC.is_file() or not PAGE.is_file():
    sys.exit("ERROR: Run this script from ~/reboot-syndicate on yeet.")

def matches(data, digest):
    return (data[:4] == b"RIFF" and data[8:12] == b"WEBP"
            and sha256(data).hexdigest().startswith(digest))

# Validate image sources completely before modifying the running project.
zip_data = None
if ARCHIVE.is_file():
    zip_data = zipfile.ZipFile(ARCHIVE)
replacements = {}
unavailable = []
try:
    for slug, digest in EXPECTED.items():
        fn = slug + ".webp"
        current = STATIC / fn
        if current.is_file() and matches(current.read_bytes(), digest):
            continue
        staged = STAGED / fn
        if staged.is_file() and matches(staged.read_bytes(), digest):
            replacements[current] = staged.read_bytes()
            continue
        name = "clear_tiles/" + fn
        if zip_data and name in zip_data.namelist():
            data = zip_data.read(name)
            if matches(data, digest):
                replacements[current] = data
                continue
        unavailable.append(fn)
finally:
    if zip_data:
        zip_data.close()

if unavailable:
    sys.exit(
        "ERROR: These files are still the old, low-resolution versions:\n  "
        + "\n  ".join(unavailable)
        + "\nCopy reboot-syndicate-14-clear-tiles.zip from your Fedora Downloads "
          "folder to ~/reboot-syndicate/ on yeet, then rerun this script. "
          "No files were changed."
    )

before_src = SRC.read_text(encoding="utf-8")
after_src = before_src
if "'image_version': image_version" not in after_src:
    old = "    return templates.TemplateResponse(request, 'marketing_detail.html', {'service':service, 'slug':slug, 'pricing':SERVICE_PRICING[slug]})"
    new = """    # Version the detail image URL by its bytes, not a hardcoded version.
    # This prevents old low-resolution browser cache entries from being reused.
    image_path = Path(__file__).resolve().parent / 'static' / 'images' / f'{slug}.webp'
    image_version = sha256(image_path.read_bytes()).hexdigest()[:12] if image_path.is_file() else 'missing'
    return templates.TemplateResponse(request, 'marketing_detail.html', {
        'service': service,
        'slug': slug,
        'pricing': SERVICE_PRICING[slug],
        'image_version': image_version,
    })"""
    if old not in after_src:
        sys.exit("ERROR: The service router differs from expected. No files were changed.")
    after_src = after_src.replace(old, new, 1)
    if "from hashlib import sha256" not in after_src:
        after_src = "from hashlib import sha256\n" + after_src
    if "from pathlib import Path" not in after_src:
        after_src = "from pathlib import Path\n" + after_src
try:
    ast.parse(after_src, filename=str(SRC))
except SyntaxError as e:
    sys.exit(f"ERROR: Invalid service router after change: {e}")

before_page = PAGE.read_text(encoding="utf-8")
after_page = before_page
old_url = "style=\"--detail-photo:url('/static/images/{{ slug }}.webp')\""
new_url = "style=\"--detail-photo:url('/static/images/{{ slug }}.webp?v={{ image_version }}')\""
if old_url in after_page:
    after_page = after_page.replace(old_url, new_url, 1)
elif new_url not in after_page:
    sys.exit("ERROR: The detail image markup differs from expected. No files changed.")

# Copy in higher-resolution assets if necessary, then patch only the two files.
stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
backups = ROOT / "backups" / ("service-detail-images-" + stamp)

def write_checked(file, data):
    old = file.read_bytes() if file.is_file() else None
    if old == data:
        return False
    if old is not None:
        dest = backups / file.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, dest)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_bytes(data)
    return True

count = 0
for image, contents in replacements.items():
    if write_checked(image, contents):
        count += 1
write_checked(SRC, after_src.encode("utf-8"))
write_checked(PAGE, after_page.encode("utf-8"))

print(f"Verified all 14 clear WebP images; replaced {count} old images.")
if backups.is_dir():
    print("Backups:", backups)
print("Service detail images now have individual cache-busting URLs.")
print("Rebuilding only the website service...")
subprocess.run(["docker", "compose", "up", "-d", "--build", "website"], check=True)

# Verify the rebuilt container has the right files and the new cache-busting code.
verify_program = """
from pathlib import Path
from hashlib import sha256
expected = """ + repr(EXPECTED) + """
for slug, digest in expected.items():
    image = Path('/srv/app/static/images') / (slug + '.webp')
    if not image.is_file() or not sha256(image.read_bytes()).hexdigest().startswith(digest):
        raise SystemExit('Wrong image in Docker: ' + slug)
template = Path('/srv/app/templates/marketing_detail.html').read_text()
source = Path('/srv/app/marketing_services.py').read_text()
assert '?v={{ image_version }}' in template, 'detail template did not update'
assert "'image_version': image_version" in source, 'detail route did not update'
print('PASS: All 14 clear images and versioned detail pages are inside Docker.')
"""
result = subprocess.run(
    ["docker", "compose", "exec", "-T", "website", "python", "-c", verify_program],
    capture_output=True, text=True
)
if result.returncode:
    sys.exit("ERROR: Container verification failed:\n" + result.stdout + result.stderr)
print(result.stdout.strip())
print("DONE. Reload a service page at https://rebootsyndicate.com/marketing/it-support")
