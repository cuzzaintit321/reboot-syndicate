# Reboot Syndicate — Search Visibility Launch Plan

Focus: **Brevard County, Florida** first, while keeping remote digital services discoverable nationally. SEO helps relevant customers find useful pages; it cannot promise particular positions, leads, or sales.

## Implemented in the codebase

- Public `/robots.txt` with a root sitemap reference.
- Dynamic `/sitemap.xml` listing the homepage, marketing overview, Brevard County guide, and all 14 marketing service pages.
- Canonical URLs on the homepage, marketing overview, county page, and 14 service pages.
- Individual service titles, descriptions, and Service JSON-LD; Organization and WebSite JSON-LD on the homepage.
- Original `/brevard-county` service guide with locally relevant information, links to real services, and realistic FAQ answers.
- Footer/About internal links to the county guide; no bulk duplicate city pages.
- Noindex directive on the consultation confirmation page.
- No business street address, fabricated client testimonials, fabricated rankings, or invented results.

## Deploy safely on yeet

Do not blindly pull this repository on the running server; that could overwrite customized local content. From `~/reboot-syndicate`:

```bash
git fetch origin main
git show origin/main:scripts/install_seo_foundation.py > /tmp/install_seo_foundation.py
python3 /tmp/install_seo_foundation.py
```

The script backs up affected files, preserves local image/hover/price modifications, builds only the website service, and validates 17 sitemap URLs and 14 SEO metadata entries inside Docker.

Then inspect:

```bash
curl -fsS https://rebootsyndicate.com/robots.txt
curl -fsS https://rebootsyndicate.com/sitemap.xml | head -c 900
curl -I https://rebootsyndicate.com/brevard-county
```

Expected landing page: `https://rebootsyndicate.com/brevard-county`

## Google Search Console (owner action)

1. Open https://search.google.com/search-console/ and add a **Domain property** for `rebootsyndicate.com` (or use URL-prefix if domain DNS verification isn't practical).
2. Verify ownership using the DNS TXT value provided by Google. Do not publish account verification secrets elsewhere.
3. Submit `https://rebootsyndicate.com/sitemap.xml` in **Sitemaps**.
4. Use **URL Inspection** for the homepage, county page, and three priority service URLs:
   - `/marketing/website-design`
   - `/marketing/local-seo`
   - `/marketing/google-business-profile`
5. Track indexing, impressions, clicks, search queries, and landing pages over time; review regularly.

## Search terms to target naturally

Prioritize high-intent terms relevant to genuine services and actual coverage:

| Priority | Search theme | Best page |
|---|---|---|
| 1 | web design Brevard County FL; website designer Titusville | `/marketing/website-design`, `/brevard-county` |
| 1 | local SEO Brevard County; SEO company Space Coast | `/marketing/local-seo` |
| 1 | Google Business Profile help Brevard County | `/marketing/google-business-profile` |
| 2 | social media management Brevard County | `/marketing/social-media` |
| 2 | Google Ads management Brevard County | `/marketing/digital-advertising` |
| 2 | IT support Titusville; small business computer support Brevard | `/marketing/it-support` |
| 3 | email marketing automation; ecommerce website design | relevant individual service pages |

Avoid promises of ranking for every search or keyword-stuffed text. Search volume and competitiveness must be confirmed with Search Console and, if useful, Keyword Planner.

## Local business relevance: ongoing work

- Confirm whether Reboot Syndicate qualifies for a Google Business Profile. Google requires **real in-person customer contact**; an online-only marketing business does not qualify. If eligible as a service-area business, enter a real verification address privately and **hide it from customers** if they don't visit it.
- Use the genuine primary business category, phone, site URL, service descriptions, and hours. Do not create profiles for fake locations.
- Put real local work examples or case studies on the website **only with client permission**, including what problem was solved and the actual scope, not invented performance metrics.
- Earn useful links through local partnerships, organizations and business associations; no link farms or paid spammy backlinks.
- After a job, invite customers to leave authentic reviews through permitted, non-incentivized requests. Never buy reviews.
- Consider one helpful guide per month based on actual questions, such as choosing a website platform, GBP categories/service areas, mobile site speed, or how to interpret website inquiries.

## Measuring actual progress

**First month:** Indexing coverage, Core Web Vitals, errors, and a starting baseline of organic search impressions and clicks.

**Month two:** Search queries showing impressions for target services and county terms; improve pages that are being discovered but aren't convincing users to click.

**Month three:** Qualified form inquiries/calls from organic search, service page performance, and examples of local partnerships and useful links.

Treat Google Search Console and the site's analytics as the source of truth, rather than ranking guarantees.
