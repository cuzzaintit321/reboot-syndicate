#!/usr/bin/env python3
"""Read-only SEO health check for the running Reboot Syndicate website.

From ~/reboot-syndicate on yeet:
  git fetch origin main
  git show origin/main:scripts/seo_live_audit.py > /tmp/seo_live_audit.py
  python3 /tmp/seo_live_audit.py

Checks crawler discovery, all sitemap URLs, title, description, canonical,
and visible primary heading. DOES NOT change files, DNS, Docker or Google.
A local check does NOT prove the site is indexed by Google.
"""
import argparse
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import ssl
import sys
import xml.etree.ElementTree as ET


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.description = ""
        self.canonical = ""
        self.robots = ""
        self.headings = []
        self._active = ""
        self.links = []
        self.schema_count = 0
        self.language = ""

    def handle_starttag(self, tag, attrs):
        info = dict(attrs)
        if tag == "html":
            self.language = info.get("lang", "")
        if tag == "title":
            self._active = "title"
        elif tag == "h1":
            self._active = "h1"
            self.headings.append("")
        elif tag == "meta":
            name = info.get("name", "").lower()
            if name == "description":
                self.description = info.get("content", "").strip()
            elif name == "robots":
                self.robots = info.get("content", "").strip()
        elif tag == "link" and "canonical" in info.get("rel", "").lower().split():
            self.canonical = info.get("href", "").strip()
        elif tag == "a":
            self.links.append(info.get("href", ""))
        elif tag == "script" and info.get("type", "").lower() == "application/ld+json":
            self.schema_count += 1

    def handle_data(self, data):
        if self._active == "title":
            self.title += data
        elif self._active == "h1" and self.headings:
            self.headings[-1] += data

    def handle_endtag(self, tag):
        if tag in ("title", "h1"):
            self._active = ""


def fetch(base, path, timeout):
    url = urljoin(base.rstrip("/") + "/", path.lstrip("/"))
    req = Request(url, headers={"User-Agent": "RebootSyndicateSEOAudit/1.0"})
    try:
        with urlopen(req, timeout=timeout) as res:
            raw = res.read(1500000)
            return (res.status, raw.decode("utf-8", errors="replace"), res.geturl(), "")
    except HTTPError as exc:
        return (exc.code, "", url, str(exc.reason))
    except (URLError, TimeoutError, OSError, ssl.SSLError) as exc:
        return (0, "", url, str(exc))


def main():
    parser = argparse.ArgumentParser(description="Inspect public SEO essentials, read-only")
    parser.add_argument("--base", default="https://rebootsyndicate.com",
                        help="Site origin to test; default is public HTTPS domain")
    parser.add_argument("--timeout", type=float, default=12,
                        help="Per-request timeout in seconds")
    args = parser.parse_args()
    base = args.base.rstrip("/")
    problems = []
    print("REBOOT SYNDICATE — READ-ONLY LIVE SEO AUDIT")
    print("Testing:", base)
    print("This tests page accessibility, NOT Google indexing or rankings.\n")

    status, robots, _, err = fetch(base, "/robots.txt", args.timeout)
    if status != 200:
        problems.append("robots.txt does not return HTTP 200")
        print(f"[FAIL] robots.txt: HTTP {status or 'connection error'} {err}")
    else:
        has_sitemap = "sitemap:" in robots.lower() and "/sitemap.xml" in robots
        print("[PASS]" if has_sitemap else "[WARN]", "robots.txt available; sitemap referenced:", has_sitemap)
        if not has_sitemap:
            problems.append("robots.txt does not reference sitemap.xml")
        if any(line.strip().lower() == "disallow: /" for line in robots.splitlines()):
            problems.append("robots.txt blocks the entire site with Disallow: /")

    status, sitemap, _, err = fetch(base, "/sitemap.xml", args.timeout)
    paths = []
    if status != 200:
        problems.append("sitemap.xml does not return HTTP 200")
        print(f"[FAIL] sitemap.xml: HTTP {status or 'connection error'} {err}")
    else:
        try:
            root = ET.fromstring(sitemap)
            locs = [e.text.strip() for e in root.iter() if e.tag.endswith("}loc") and e.text]
            paths = [urlparse(url).path or "/" for url in locs]
            print(f"[PASS] sitemap.xml: {len(locs)} URLs")
            if len(locs) != 17:
                problems.append(f"Sitemap has {len(locs)} URLs; expected 17")
            if len(set(locs)) != len(locs):
                problems.append("Sitemap has duplicate URLs")
            if any(urlparse(url).netloc not in ("rebootsyndicate.com", "www.rebootsyndicate.com") for url in locs):
                problems.append("Sitemap includes an unexpected host")
        except ET.ParseError as exc:
            problems.append("Sitemap XML cannot be parsed: " + str(exc))
            print("[FAIL] sitemap.xml cannot be parsed:", exc)

    if not paths:
        paths = ["/", "/brevard-county", "/marketing", "/marketing/website-design",
                 "/marketing/local-seo", "/marketing/google-business-profile",
                 "/marketing/it-support"]

    print("\nPAGE CHECKS")
    seen_titles = Counter()
    seen_descriptions = Counter()
    for path in paths:
        status, body, final_url, err = fetch(base, path, args.timeout)
        if status != 200:
            print(f"[FAIL] {path}: HTTP {status or 'connection error'} {err}")
            problems.append(f"{path} unavailable (HTTP {status})")
            continue
        doc = Page()
        doc.feed(body)
        doc.title = " ".join(doc.title.split())
        desc = " ".join(doc.description.split())
        canonical_path = urlparse(doc.canonical).path or "/"
        expected_path = path.rstrip("/") or "/"
        issues = []
        if not doc.title:
            issues.append("missing title")
        if not desc:
            issues.append("missing description")
        if not doc.canonical:
            issues.append("missing canonical")
        elif canonical_path != expected_path:
            issues.append("canonical points to a different path")
        if doc.canonical and urlparse(doc.canonical).netloc != "rebootsyndicate.com":
            issues.append("canonical host differs")
        if len(doc.headings) != 1:
            issues.append("expected one H1, found " + str(len(doc.headings)))
        if "noindex" in doc.robots.lower():
            issues.append("noindex detected")
        if not doc.language:
            issues.append("html lang missing")
        if (path == "/" or path.startswith("/marketing/")) and not doc.schema_count:
            issues.append("expected structured data missing")
        seen_titles[doc.title] += 1
        seen_descriptions[desc] += 1
        status_text = "PASS" if not issues else "WARN"
        print(f"[{status_text}] {path} — {doc.title[:88]}")
        if issues:
            print("       " + "; ".join(issues))
            problems.extend(f"{path}: {issue}" for issue in issues)

    for title, count in seen_titles.items():
        if title and count > 1:
            problems.append(f"Duplicate title ({count} pages): {title}")
    for desc, count in seen_descriptions.items():
        if desc and count > 1:
            problems.append(f"Duplicate meta description ({count} pages): {desc[:90]}")

    status, body, _, err = fetch(base, "/thanks", args.timeout)
    if status == 200:
        check = Page()
        check.feed(body)
        if "noindex" not in check.robots.lower():
            problems.append("Thank-you page should be marked noindex")

    print("\nRESULT")
    if problems:
        print("Issues to review:", len(problems))
        for problem in problems:
            print(" -", problem)
    else:
        print("PASS: No issues detected in the tested technical SEO checks.")
    print("\nNEXT: Verify ownership in Google Search Console, submit sitemap.xml,")
    print("and use URL Inspection to see whether Google has actually indexed pages.")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
