"""
Meta Ad Library Scraper
Purpose: Pull competitor ads from the Meta Ad Library by keyword or Page ID.
         Shows active ads, copy, creative formats, estimated run duration,
         and publishing pages. Useful for competitive research and creative
         inspiration before launching new campaigns.

         The Ad Library API is public and does not require a business token,
         but using an access token increases rate limits and data access.

Setup:
    Requires environment variables:
        META_ACCESS_TOKEN  (optional but recommended for higher rate limits)

    Install dependency:
        pip3 install facebook-business python-dotenv requests

Usage:
    python3 scripts/meta_ad_library_scraper.py --keyword "custom furniture"
    python3 scripts/meta_ad_library_scraper.py --keyword "dentist Toronto" --country CA
    python3 scripts/meta_ad_library_scraper.py --page-id 123456789
    python3 scripts/meta_ad_library_scraper.py --keyword "law firm" --limit 20 --save

    --keyword     Search term to find ads (searches ad copy and page name)
    --page-id     Pull all active ads from a specific Facebook Page ID
    --country     ISO country code to filter (default: US)
    --limit       Max ads to return (default: 25, max: 100)
    --save        Save results to clients/ folder as a markdown file
    --active-only Only show currently active ads (default: True)

Output per ad:
    - Page name and ID
    - Ad creative type (image, video, carousel)
    - Ad copy (body text, headline, CTA)
    - Start date and estimated run duration
    - Countries targeted

Changelog:
    2026-03-21  Initial version — keyword and page-id search, copy extraction,
                duration calculation, markdown save option.
"""

import argparse
import os
import sys
import json
import requests
from datetime import date, datetime
from dotenv import load_dotenv

load_dotenv()

# ─── CONSTANTS ────────────────────────────────────────────────────────────────

AD_LIBRARY_URL = "https://graph.facebook.com/v19.0/ads_archive"

AD_FIELDS = [
    "id",
    "ad_creation_time",
    "ad_creative_bodies",
    "ad_creative_link_captions",
    "ad_creative_link_descriptions",
    "ad_creative_link_titles",
    "ad_delivery_start_time",
    "ad_delivery_stop_time",
    "ad_snapshot_url",
    "currency",
    "delivery_by_region",
    "estimated_audience_size",
    "impressions",
    "page_id",
    "page_name",
    "publisher_platforms",
    "spend",
]

CREATIVE_TYPE_ICONS = {
    "facebook": "FB",
    "instagram": "IG",
    "messenger": "MSG",
    "audience_network": "AN",
}

# ─── FETCH ────────────────────────────────────────────────────────────────────

def fetch_ads(keyword=None, page_id=None, country="US", limit=25, active_only=True):
    """
    Fetch ads from Meta Ad Library API.
    Returns list of ad dicts.
    """
    token = os.environ.get("HOSKI_META_ACCESS_TOKEN") or os.environ.get("META_ACCESS_TOKEN")
    if not token:
        print("Warning: META_ACCESS_TOKEN not set. Rate limits will be lower.")
        print("         Set the token in your .env file for better results.\n")
        token = None

    params: dict = {
        "ad_type":              "ALL",
        "ad_reached_countries":  f"['{country}']",
        "fields":               ",".join(AD_FIELDS),
        "limit":                min(limit, 100),
    }

    if active_only:
        params["ad_active_status"] = "ACTIVE"

    if keyword:
        params["search_terms"] = keyword
    elif page_id:
        params["search_page_ids"] = f"['{page_id}']"
    else:
        print("Error: provide --keyword or --page-id")
        sys.exit(1)

    if token:
        params["access_token"] = token

    try:
        resp = requests.get(AD_LIBRARY_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        sys.exit(1)

    if "error" in data:
        err = data["error"]
        print(f"API error {err.get('code')}: {err.get('message')}")
        sys.exit(1)

    ads = data.get("data", [])

    # Paginate if needed and limit not reached
    while "paging" in data and data["paging"].get("next") and len(ads) < limit:
        try:
            resp  = requests.get(data["paging"]["next"], timeout=30)
            data  = resp.json()
            ads  += data.get("data", [])
        except requests.RequestException:
            break

    return ads[:limit]


# ─── PARSE ────────────────────────────────────────────────────────────────────

def parse_duration(start_str, stop_str=None):
    """Calculate how long an ad has been/was running."""
    if not start_str:
        return "Unknown"
    try:
        start = datetime.fromisoformat(start_str.replace("Z", "+00:00")).date()
        end   = datetime.fromisoformat(stop_str.replace("Z", "+00:00")).date() if stop_str else date.today()
        days  = (end - start).days
        if days < 7:
            return f"{days}d"
        elif days < 30:
            return f"{days // 7}w {days % 7}d"
        else:
            months = days // 30
            rem    = days % 30
            return f"{months}mo {rem}d" if rem else f"{months}mo"
    except (ValueError, TypeError):
        return "Unknown"


def parse_creative_type(ad):
    """Infer creative type from available fields."""
    bodies    = ad.get("ad_creative_bodies", [])
    titles    = ad.get("ad_creative_link_titles", [])
    captions  = ad.get("ad_creative_link_captions", [])

    if len(bodies) > 1 or len(titles) > 1:
        return "Carousel"
    if titles or captions:
        return "Image / Link"
    return "Image / Video"


def parse_platforms(ad):
    platforms = ad.get("publisher_platforms", [])
    return ", ".join(CREATIVE_TYPE_ICONS.get(p, p.title()) for p in platforms) or "Unknown"


def parse_audience_size(ad):
    est = ad.get("estimated_audience_size", {})
    if not est:
        return "Unknown"
    lo = est.get("lower_bound", 0)
    hi = est.get("upper_bound", 0)
    if lo >= 1_000_000:
        return f"{lo/1_000_000:.1f}M-{hi/1_000_000:.1f}M"
    elif lo >= 1_000:
        return f"{lo/1_000:.0f}K-{hi/1_000:.0f}K"
    return f"{lo:,}-{hi:,}"


# ─── PRINT & SAVE ─────────────────────────────────────────────────────────────

def format_ad(ad, index, mode="print"):
    """Format a single ad for print or markdown output."""
    page_name    = ad.get("page_name", "Unknown Page")
    page_id      = ad.get("page_id", "")
    creative_type = parse_creative_type(ad)
    platforms    = parse_platforms(ad)
    start_time   = ad.get("ad_delivery_start_time", "")
    stop_time    = ad.get("ad_delivery_stop_time", "")
    duration     = parse_duration(start_time, stop_time)
    start_str    = start_time[:10] if start_time else "Unknown"
    snapshot_url = ad.get("ad_snapshot_url", "")
    audience_size = parse_audience_size(ad)

    # Copy
    bodies     = ad.get("ad_creative_bodies", [])
    titles     = ad.get("ad_creative_link_titles", [])
    captions   = ad.get("ad_creative_link_captions", [])
    descs      = ad.get("ad_creative_link_descriptions", [])

    body_str    = bodies[0][:280]    if bodies    else "(no body copy)"
    title_str   = titles[0][:100]    if titles    else ""
    caption_str = captions[0][:100]  if captions  else ""
    desc_str    = descs[0][:150]     if descs     else ""

    # Carousel items (if multiple)
    carousel_items = []
    for i in range(1, min(len(bodies), len(titles) + 1, 5)):
        item_body  = bodies[i][:120]  if i < len(bodies)  else ""
        item_title = titles[i][:80]   if i < len(titles)  else ""
        if item_body or item_title:
            carousel_items.append((item_title, item_body))

    if mode == "markdown":
        lines = [
            f"## Ad {index}: {page_name}",
            f"",
            f"| Field | Value |",
            f"|---|---|",
            f"| Page | {page_name} (ID: {page_id}) |",
            f"| Format | {creative_type} |",
            f"| Platforms | {platforms} |",
            f"| Started | {start_str} |",
            f"| Running for | {duration} |",
            f"| Est. audience | {audience_size} |",
            f"",
            f"**Body copy:**",
            f"> {body_str}",
            f"",
        ]
        if title_str:
            lines.append(f"**Headline:** {title_str}")
        if caption_str:
            lines.append(f"**Caption:** {caption_str}")
        if desc_str:
            lines.append(f"**Description:** {desc_str}")
        if carousel_items:
            lines.append(f"\n**Carousel cards:**")
            for i, (t, b) in enumerate(carousel_items, 2):
                lines.append(f"- Card {i}: {t} — {b}")
        if snapshot_url:
            lines.append(f"\n[View Ad]({snapshot_url})")
        lines.append("")
        return "\n".join(lines)

    else:  # print mode
        sep = "─" * 55
        lines = [
            f"\n{sep}",
            f"Ad {index}: {page_name}  (ID: {page_id})",
            f"  Format: {creative_type}  |  Platforms: {platforms}  |  Started: {start_str}  |  Running: {duration}",
            f"  Est. audience: {audience_size}",
            f"  Body: {body_str}",
        ]
        if title_str:
            lines.append(f"  Headline: {title_str}")
        if caption_str:
            lines.append(f"  Caption: {caption_str}")
        if desc_str:
            lines.append(f"  Description: {desc_str}")
        if carousel_items:
            for i, (t, b) in enumerate(carousel_items, 2):
                lines.append(f"  Card {i}: {t} — {b}")
        if snapshot_url:
            lines.append(f"  Preview: {snapshot_url}")
        return "\n".join(lines)


def save_markdown(ads, keyword, page_id, country, output_path):
    """Save ad results as a markdown file."""
    today = date.today().strftime("%Y-%m-%d")
    search_label = f'keyword "{keyword}"' if keyword else f"Page ID {page_id}"

    lines = [
        f"# Meta Ad Library — {search_label}",
        f"",
        f"**Date:** {today}  ",
        f"**Country:** {country}  ",
        f"**Ads found:** {len(ads)}  ",
        f"",
        "---",
        "",
    ]

    for i, ad in enumerate(ads, 1):
        lines.append(format_ad(ad, i, mode="markdown"))
        lines.append("---\n")

    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\nSaved to: {output_path}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Meta Ad Library scraper — competitor ad research by keyword or Page ID"
    )
    parser.add_argument("--keyword",     help="Search term to find ads in the Meta Ad Library")
    parser.add_argument("--page-id",     help="Facebook Page ID to pull all ads from a specific advertiser")
    parser.add_argument("--country",     default="US",
                        help="ISO country code to filter ads (default: US). Examples: CA, GB, AU")
    parser.add_argument("--limit",       type=int, default=25,
                        help="Max number of ads to return (default: 25, max: 100)")
    parser.add_argument("--save",        action="store_true",
                        help="Save results as a markdown file in the current directory")
    parser.add_argument("--output",      default="",
                        help="Custom output file path (used with --save)")
    parser.add_argument("--all-status",  action="store_true",
                        help="Include inactive/completed ads (default: active only)")
    args = parser.parse_args()

    if not args.keyword and not args.page_id:
        print("Error: provide --keyword or --page-id")
        parser.print_help()
        sys.exit(1)

    search_label = f'"{args.keyword}"' if args.keyword else f"Page {args.page_id}"
    active_only  = not args.all_status

    print(f"\nSearching Meta Ad Library for {search_label} in {args.country}...")
    print(f"Active only: {active_only}  |  Limit: {args.limit}")

    ads = fetch_ads(
        keyword     = args.keyword,
        page_id     = args.page_id,
        country     = args.country,
        limit       = args.limit,
        active_only = active_only,
    )

    if not ads:
        print("No ads found. Try a different keyword, Page ID, or country.")
        return

    print(f"\nFound {len(ads)} ad(s):\n")

    for i, ad in enumerate(ads, 1):
        print(format_ad(ad, i, mode="print"))

    # Creative format summary
    formats: dict = {}
    for ad in ads:
        fmt = parse_creative_type(ad)
        formats[fmt] = formats.get(fmt, 0) + 1

    pages: dict = {}
    for ad in ads:
        pname = ad.get("page_name", "Unknown")
        pages[pname] = pages.get(pname, 0) + 1

    print(f"\n{'='*55}")
    print(f"SUMMARY — {len(ads)} ads for {search_label} ({args.country})")
    print(f"{'='*55}")
    print(f"  Formats: " + ", ".join(f"{v}x {k}" for k, v in sorted(formats.items(), key=lambda x: -x[1])))
    print(f"  Top advertisers:")
    for pname, count in sorted(pages.items(), key=lambda x: -x[1])[:5]:
        print(f"    {count}x  {pname}")

    # Duration analysis
    durations = []
    for ad in ads:
        start = ad.get("ad_delivery_start_time", "")
        stop  = ad.get("ad_delivery_stop_time", "")
        if start:
            try:
                s   = datetime.fromisoformat(start.replace("Z", "+00:00")).date()
                e   = datetime.fromisoformat(stop.replace("Z", "+00:00")).date() if stop else date.today()
                durations.append((e - s).days)
            except (ValueError, TypeError):
                pass
    if durations:
        avg_days = sum(durations) / len(durations)
        max_days = max(durations)
        print(f"  Avg run duration: {avg_days:.0f} days  |  Longest: {max_days} days")
        print(f"  Ads running 30+ days (proven): {sum(1 for d in durations if d >= 30)}")

    print(f"{'='*55}")

    if args.save:
        output_path = args.output or f"meta_ad_library_{args.keyword or args.page_id}_{date.today()}.md"
        output_path = output_path.replace(" ", "_").replace('"', "")
        save_markdown(ads, args.keyword, args.page_id, args.country, output_path)


if __name__ == "__main__":
    main()
