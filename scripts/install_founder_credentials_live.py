#!/usr/bin/env python3
"""Safely install founder certification list into the live Reboot Syndicate checkout.

Patches only the About section, scoped stylesheet block, and three brand SVGs.
Preserves local edits to all other templates, routes, and Docker configuration.
No git pull/reset is performed. Keeps rollback copies under /tmp.
"""
from __future__ import annotations

import re
import shutil
import sys
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path.cwd()
BASE = "https://raw.githubusercontent.com/cuzzaintit321/reboot-syndicate/main"
INDEX = ROOT / "app/templates/index.html"
CSS = ROOT / "app/static/site.css"
LOGOS = ("google", "hootsuite", "mailchimp")
CSS_BEGIN = "/* R/S credentials list - begin */"
CSS_END = "/* R/S credentials list - end */"
ABOUT_PATTERN = re.compile(
    r'<section\b[^>]*\bid="about"[^>]*>[\s\S]*?</section>',
    re.IGNORECASE,
)


def download(path: str) -> str:
    request = Request(f"{BASE}/{path}", headers={"User-Agent": "RebootSyndicateCertInstaller/1.0"})
    with urlopen(request, timeout=25) as response:
        return response.read().decode("utf-8")


def extract_once(pattern: re.Pattern[str], content: str, label: str) -> str:
    matches = pattern.findall(content)
    if len(matches) != 1:
        raise RuntimeError(f"Expected one {label}; found {len(matches)}. No changes made.")
    return matches[0]


def main() -> None:
    if not INDEX.is_file() or not CSS.is_file():
        raise RuntimeError("Run from ~/reboot-syndicate (missing app/templates/index.html or app/static/site.css).")

    source_html = download("app/templates/index.html")
    source_css = download("app/static/site.css")
    section = extract_once(ABOUT_PATTERN, source_html, "new About section")
    if section.count('class="rs-about-cert-copy"') != 6:
        raise RuntimeError("Remote About section does not contain six credential entries.")

    block_pattern = re.compile(re.escape(CSS_BEGIN) + r"[\s\S]*?" + re.escape(CSS_END))
    css_block = extract_once(block_pattern, source_css, "credential stylesheet block")

    local_html = INDEX.read_text(encoding="utf-8")
    local_css = CSS.read_text(encoding="utf-8")
    extract_once(ABOUT_PATTERN, local_html, "existing About section")
    changed_html = ABOUT_PATTERN.sub(lambda _: section, local_html, count=1)
    # Force browsers to fetch the updated homepage CSS after deployment.
    changed_html = re.sub(
        r'href="/static/site\.css(?:\?[^"]*)?"',
        'href="/static/site.css?v=about-mobile-20261102"',
        changed_html,
        count=1,
    )

    existing_blocks = block_pattern.findall(local_css)
    if len(existing_blocks) > 1:
        raise RuntimeError("Duplicate credential style blocks detected. No changes made.")
    if existing_blocks:
        changed_css = block_pattern.sub(lambda _: css_block, local_css, count=1)
    else:
        changed_css = local_css.rstrip() + "\n\n" + css_block + "\n"

    updates: dict[Path, str] = {INDEX: changed_html, CSS: changed_css}
    for logo in LOGOS:
        body = download(f"app/static/brands/{logo}.svg")
        if not body.lstrip().startswith("<svg") or "<path" not in body or len(body) > 30000:
            raise RuntimeError(f"Invalid SVG for {logo}; no changes made.")
        updates[ROOT / "app/static/brands" / f"{logo}.svg"] = body

    changes = {path: data for path, data in updates.items()
               if not path.exists() or path.read_text(encoding="utf-8") != data}
    if not changes:
        print("Founder credentials already installed; no changes necessary.")
        return

    backup = Path(tempfile.mkdtemp(prefix="rs-credentials-backup-", dir="/tmp"))
    prior = {}
    for path in changes:
        if path.exists():
            saved = backup / path.relative_to(ROOT)
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, saved)
            prior[path] = saved
        else:
            prior[path] = None
    try:
        for path, data in changes.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(data, encoding="utf-8")
    except Exception:
        for path, saved in prior.items():
            if saved is None:
                path.unlink(missing_ok=True)
            else:
                shutil.copy2(saved, path)
        raise

    print(f"Installed {len(changes)} updated site files.")
    print("Original About section restored with 6 compact certification entries and issuer logos.")
    print(f"Backup of replaced files: {backup}")
    print("Next: docker compose up -d --build website")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"INSTALL FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
