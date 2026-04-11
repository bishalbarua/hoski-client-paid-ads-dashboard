"""
Merchant Center Feed Diagnostics
Purpose: Pulls product feed status, item-level issues, and feed diagnostics
         from Google Merchant Center via the Content API for Shopping.

         Surfaces:
           - Feed-level processing errors and warnings
           - Product disapprovals and their reasons
           - Item-level issues grouped by severity and description
           - Checkout URL errors and other critical feed problems

         Designed to give the same visibility as the Merchant Center UI
         without having to open a browser.

Setup:
    Uses the same OAuth credentials as Google Ads scripts (client_id,
    client_secret, refresh_token from .env).

    Add the Merchant Center account ID to .env:
        MERCHANT_CENTER_EJPR=5339948222

    Or pass it directly via --merchant-id.

Usage:
    python3 scripts/merchant_center_diagnostics.py
    python3 scripts/merchant_center_diagnostics.py --merchant-id 5339948222
    python3 scripts/merchant_center_diagnostics.py --issues-only
    python3 scripts/merchant_center_diagnostics.py --max-products 500

Output:
    Prints a markdown report to stdout and saves to:
        clients/<folder>/analysis/merchant_center_diagnostics_<date>.md

Changelog:
    2026-04-10  Initial version.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date

from pathlib import Path

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# ─── KNOWN MERCHANT CENTER IDs ────────────────────────────────────────────────

MERCHANT_ACCOUNTS: dict[str, str] = {
    "Estate Jewelry Priced Right": os.environ.get("MERCHANT_CENTER_EJPR", "5339948222"),
}

# ─── AUTH ─────────────────────────────────────────────────────────────────────

def _build_service():
    # Do not pass scopes here — the refresh token already carries the granted scopes.
    # Passing scopes would cause Google to re-validate them against the token,
    # which fails if the consent screen does not explicitly list the content scope.
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
        client_id=os.environ["GOOGLE_ADS_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
    )
    creds.refresh(Request())
    return build("content", "v2.1", credentials=creds, cache_discovery=False)


# ─── DATA FETCHING ────────────────────────────────────────────────────────────

def fetch_account_info(service, merchant_id: str) -> dict:
    try:
        return service.accounts().get(merchantId=merchant_id, accountId=merchant_id).execute()
    except HttpError:
        return {}


def fetch_datafeeds(service, merchant_id: str) -> list[dict]:
    feeds = []
    request = service.datafeeds().list(merchantId=merchant_id)
    while request is not None:
        resp = request.execute()
        feeds.extend(resp.get("resources", []))
        request = service.datafeeds().list_next(request, resp)
    return feeds


def fetch_datafeed_statuses(service, merchant_id: str) -> list[dict]:
    statuses = []
    request = service.datafeedstatuses().list(merchantId=merchant_id)
    while request is not None:
        resp = request.execute()
        statuses.extend(resp.get("resources", []))
        request = service.datafeedstatuses().list_next(request, resp)
    return statuses


def fetch_product_statuses(service, merchant_id: str, max_products: int) -> list[dict]:
    """Fetch product statuses — each entry includes item-level issues."""
    statuses = []
    request = service.productstatuses().list(
        merchantId=merchant_id,
        maxResults=250,
        includeAttributes=False,
    )
    while request is not None and len(statuses) < max_products:
        resp = request.execute()
        batch = resp.get("resources", [])
        statuses.extend(batch)
        request = service.productstatuses().list_next(request, resp)
    return statuses[:max_products]


# ─── ANALYSIS ─────────────────────────────────────────────────────────────────

def _severity_rank(s: str) -> int:
    return {"error": 0, "warning": 1, "suggestion": 2}.get(s.lower(), 3)


def analyze_product_statuses(statuses: list[dict]) -> dict:
    """Aggregate issue counts and collect worst offenders."""
    total = len(statuses)
    disapproved = 0
    limited = 0
    approved = 0

    # issue_description -> {severity, count, example_ids}
    issue_map: dict[str, dict] = {}
    # products with at least one error-level issue
    error_products: list[dict] = []

    for ps in statuses:
        dest_statuses = ps.get("destinationStatuses", [])
        item_issues = ps.get("itemLevelIssues", [])

        # Determine approval state across all destinations
        states = {d.get("status", "") for d in dest_statuses}
        if "disapproved" in states:
            disapproved += 1
        elif "demoted" in states or "limited" in states:
            limited += 1
        else:
            approved += 1

        # Aggregate issues
        has_error = False
        for issue in item_issues:
            desc = issue.get("description", "Unknown issue")
            sev = issue.get("severity", "suggestion").lower()
            code = issue.get("code", "")
            servability = issue.get("servability", "")

            key = f"{code}|{desc}"
            if key not in issue_map:
                issue_map[key] = {
                    "description": desc,
                    "severity": sev,
                    "code": code,
                    "servability": servability,
                    "count": 0,
                    "example_ids": [],
                }
            issue_map[key]["count"] += 1
            if len(issue_map[key]["example_ids"]) < 3:
                product_id = ps.get("productId", "")
                # Extract just the item ID portion (after the last colon)
                short_id = product_id.split(":")[-1] if ":" in product_id else product_id
                issue_map[key]["example_ids"].append(short_id)

            if sev == "error":
                has_error = True

        if has_error:
            error_products.append(ps)

    # Sort issues: errors first, then by count desc
    sorted_issues = sorted(
        issue_map.values(),
        key=lambda x: (_severity_rank(x["severity"]), -x["count"]),
    )

    return {
        "total": total,
        "disapproved": disapproved,
        "limited": limited,
        "approved": approved,
        "issues": sorted_issues,
        "error_products": error_products[:10],  # cap for report length
    }


# ─── FORMATTING ───────────────────────────────────────────────────────────────

def _sev_icon(severity: str) -> str:
    return {"error": "🚨", "warning": "⚠️", "suggestion": "💡"}.get(severity.lower(), "ℹ️")


def _md_escape(v) -> str:
    return str(v).replace("|", "\\|")


def render_report(
    account_name: str,
    merchant_id: str,
    feeds: list[dict],
    feed_statuses: list[dict],
    product_analysis: dict,
    run_date: date,
    issues_only: bool,
) -> str:
    lines: list[str] = []

    lines.append(f"# Merchant Center Diagnostics — {account_name}")
    lines.append(f"**Merchant ID:** {merchant_id}  ")
    lines.append(f"**Run date:** {run_date}  ")
    lines.append(f"**Products scanned:** {product_analysis['total']}")
    lines.append("")

    # ── Product Status Summary ──
    lines.append("## Product Status Summary")
    lines.append("")
    lines.append("| Status | Count |")
    lines.append("|---|---|")
    lines.append(f"| Approved | {product_analysis['approved']} |")
    lines.append(f"| Limited / Demoted | {product_analysis['limited']} |")
    lines.append(f"| Disapproved | {product_analysis['disapproved']} |")
    lines.append(f"| **Total** | **{product_analysis['total']}** |")
    lines.append("")

    # ── Feed Status ──
    lines.append("## Feed Status")
    lines.append("")

    status_by_id = {str(s.get("datafeedId")): s for s in feed_statuses}

    if not feeds:
        lines.append("_No feeds found._")
    else:
        lines.append("| Feed | ID | Format | Status | Items OK | Errors | Warnings |")
        lines.append("|---|---|---|---|---|---|---|")
        for feed in feeds:
            fid = str(feed.get("id", ""))
            name = feed.get("name", "—")
            fmt = feed.get("format", {}).get("fileEncoding", "—")
            st = status_by_id.get(fid, {})
            processing = st.get("processingStatus", "—")
            items_valid = st.get("itemsValid", "—")
            items_total = st.get("itemsTotal", "—")
            errors = len(st.get("errors", []))
            warnings = len(st.get("warnings", []))
            ok_str = f"{items_valid}/{items_total}" if items_total != "—" else "—"
            lines.append(
                f"| {_md_escape(name)} | {fid} | {fmt} | {processing} "
                f"| {ok_str} | {errors} | {warnings} |"
            )
        lines.append("")

        # Feed-level errors and warnings
        for feed in feeds:
            fid = str(feed.get("id", ""))
            fname = feed.get("name", fid)
            st = status_by_id.get(fid, {})
            feed_errors = st.get("errors", [])
            feed_warnings = st.get("warnings", [])

            if feed_errors or feed_warnings:
                lines.append(f"### Feed Issues: {fname}")
                lines.append("")
                for err in feed_errors:
                    lines.append(f"- 🚨 **Error** — {err.get('message', '')} "
                                 f"(count: {err.get('count', '?')})")
                for warn in feed_warnings:
                    lines.append(f"- ⚠️ **Warning** — {warn.get('message', '')} "
                                 f"(count: {warn.get('count', '?')})")
                lines.append("")

    # ── Item-Level Issues ──
    lines.append("## Item-Level Issues")
    lines.append("")

    issues = product_analysis["issues"]
    if not issues:
        lines.append("_No item-level issues found._")
    else:
        lines.append("| Severity | Code | Issue | Affected Products | Servability |")
        lines.append("|---|---|---|---|---|")
        for issue in issues:
            icon = _sev_icon(issue["severity"])
            sev = issue["severity"].capitalize()
            code = issue.get("code", "—")
            desc = _md_escape(issue["description"])
            count = issue["count"]
            serv = issue.get("servability", "—")
            lines.append(f"| {icon} {sev} | `{code}` | {desc} | {count} | {serv} |")
        lines.append("")

        # Drill into error-level issues with examples
        error_issues = [i for i in issues if i["severity"] == "error"]
        if error_issues:
            lines.append("### Error Issue Details")
            lines.append("")
            for issue in error_issues:
                lines.append(f"**{issue['description']}**  ")
                lines.append(f"Code: `{issue['code']}` | Affects: {issue['count']} products")
                if issue["example_ids"]:
                    examples = ", ".join(issue["example_ids"][:3])
                    lines.append(f"Example product IDs: {examples}")
                lines.append("")

    if not issues_only:
        # ── Worst Offenders ──
        error_prods = product_analysis["error_products"]
        if error_prods:
            lines.append("## Products With Errors (Sample)")
            lines.append("")
            lines.append("| Product ID | Title | Destinations | Issues |")
            lines.append("|---|---|---|---|")
            for ps in error_prods:
                pid = ps.get("productId", "—").split(":")[-1]
                title = _md_escape(ps.get("title", "—")[:60])
                dests = ", ".join(
                    d.get("approvedCountries", [""])[0] if d.get("approvedCountries") else d.get("status", "")
                    for d in ps.get("destinationStatuses", [])[:2]
                )
                issue_count = len(ps.get("itemLevelIssues", []))
                lines.append(f"| {pid} | {title} | {dests or '—'} | {issue_count} |")
            lines.append("")

    lines.append("---")
    lines.append(f"_Generated by merchant_center_diagnostics.py on {run_date}_")
    lines.append("")

    return "\n".join(lines)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Merchant Center feed diagnostics")
    parser.add_argument(
        "--merchant-id",
        default=None,
        help="Merchant Center account ID (default: Estate Jewelry Priced Right)",
    )
    parser.add_argument(
        "--account-name",
        default=None,
        help="Display name for the account (default: auto-detected or 'Unknown')",
    )
    parser.add_argument(
        "--issues-only",
        action="store_true",
        help="Only show products and feeds with issues",
    )
    parser.add_argument(
        "--max-products",
        type=int,
        default=1000,
        help="Max products to scan (default: 1000)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory to save the report (default: auto from client_registry)",
    )
    args = parser.parse_args()

    # Resolve merchant ID and name
    if args.merchant_id:
        merchant_id = args.merchant_id
        account_name = args.account_name or "Unknown"
        # Try reverse lookup
        for name, mid in MERCHANT_ACCOUNTS.items():
            if mid == merchant_id:
                account_name = name
                break
    else:
        # Default to EJPR
        account_name = "Estate Jewelry Priced Right"
        merchant_id = MERCHANT_ACCOUNTS[account_name]

    print(f"Connecting to Merchant Center: {account_name} ({merchant_id})...")

    try:
        service = _build_service()
    except Exception as e:
        print(f"Auth error: {e}")
        sys.exit(1)

    print("Fetching datafeeds...")
    feeds = fetch_datafeeds(service, merchant_id)
    print(f"  Found {len(feeds)} feed(s)")

    print("Fetching feed statuses...")
    feed_statuses = fetch_datafeed_statuses(service, merchant_id)

    print(f"Fetching product statuses (up to {args.max_products})...")
    product_statuses = fetch_product_statuses(service, merchant_id, args.max_products)
    print(f"  Retrieved {len(product_statuses)} products")

    print("Analyzing issues...")
    product_analysis = analyze_product_statuses(product_statuses)

    run_date = date.today()
    report = render_report(
        account_name=account_name,
        merchant_id=merchant_id,
        feeds=feeds,
        feed_statuses=feed_statuses,
        product_analysis=product_analysis,
        run_date=run_date,
        issues_only=args.issues_only,
    )

    print("\n" + report)

    # Resolve output directory
    if args.output_dir:
        out_dir = Path(args.output_dir)
    else:
        try:
            from scripts.client_registry import get_client_analysis_dir
            out_dir = get_client_analysis_dir(account_name)
        except (KeyError, ImportError):
            out_dir = Path(__file__).resolve().parent.parent / "clients" / f"{account_name} ({merchant_id})" / "analysis"

    from scripts.report_io import write_markdown_report
    filename = f"merchant_center_diagnostics_{run_date}.md"
    out_path = write_markdown_report(out_dir / filename, report)
    print(f"\nReport saved to: {out_path}")


if __name__ == "__main__":
    main()
