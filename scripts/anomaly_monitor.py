"""
Anomaly Monitor
Purpose: Daily scan of all Google Ads client accounts. Flags critical anomalies
         across conversions, spend, traffic quality, and ad health — before
         clients notice them. Saves a structured severity report to
         reports/anomaly-YYYY-MM-DD.md.

         Run this every morning to catch problems that cost money if missed.

Setup:
    Requires environment variables in .env:
        GOOGLE_ADS_DEVELOPER_TOKEN
        GOOGLE_ADS_CLIENT_ID
        GOOGLE_ADS_CLIENT_SECRET
        GOOGLE_ADS_REFRESH_TOKEN
        GOOGLE_ADS_CUSTOMER_ID  (MCC account ID)

    Optional: configure thresholds in scripts/anomaly_config.py

Usage:
    python3 scripts/anomaly_monitor.py                             # all clients
    python3 scripts/anomaly_monitor.py --customer-id 5544702166   # single client
    python3 scripts/anomaly_monitor.py --save                     # save to reports/

Anomaly Checks:
    CONVERSIONS
        CRITICAL  0 conversions yesterday for account averaging >0.5 conv/day
        CRITICAL  Yesterday conversions down >50% vs 7-day daily average

    SPEND
        WARNING   Total account spend >120% or <20% of daily budget yesterday
        WARNING   Single campaign consuming >80% of total account spend

    TRAFFIC QUALITY
        WARNING   CTR dropped >30% WoW (relative)
        WARNING   Search Impression Share dropped >15 points WoW (absolute)
        WARNING   Average CPC spiked >40% WoW (relative)

    AD HEALTH
        CRITICAL  Any ad disapproved in an active campaign/ad group
        WARNING   Active ad group with 0 impressions in 7 days

Changelog:
    2026-03-23  Initial version — conversion drops, spend pacing, traffic quality
                WoW trends, disapprovals, zero-impression ad groups, file output.
"""

import argparse
import os
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

load_dotenv()

# ─── CLIENT REGISTRY ─────────────────────────────────────────────────────────

ALL_CLIENTS = {
    "Anand Desai Law Firm":                 "5865660247",
    "Dentiste":                             "3857223862",
    "Estate Jewelry Priced Right":          "7709532223",
    "FaBesthetics":                         "9304117954",
    "GDM Google Ads":                       "7087867966",
    "Hoski.ca":                             "5544702166",
    "New Norseman":                         "3720173680",
    "Park Road Custom Furniture and Decor": "7228467515",
    "Serenity Familycare":                  "8134824884",
    "Synergy Spine & Nerve Center":         "7628667762",
    "Texas FHC":                            "8159668041",
    "Voit Dental (1)":                      "5216656756",
    "Voit Dental (2)":                      "5907367258",
}

# ─── LOAD THRESHOLDS ─────────────────────────────────────────────────────────

try:
    from anomaly_config import (
        CONV_ZERO_MIN_DAILY_AVG, CONV_DROP_THRESHOLD,
        SPEND_OVERPACE_THRESHOLD, SPEND_UNDERPACE_THRESHOLD,
        SPEND_CONCENTRATION_THRESHOLD,
        CTR_DROP_THRESHOLD, IS_DROP_THRESHOLD, CPC_SPIKE_THRESHOLD,
        ZERO_IMPRESSION_DAYS, MIN_ACCOUNT_SPEND_30D,
        MAX_ZERO_IMPRESSION_ALERTS, CLIENT_OVERRIDES,
    )
except ImportError:
    CONV_ZERO_MIN_DAILY_AVG       = 0.5
    CONV_DROP_THRESHOLD           = 0.50
    SPEND_OVERPACE_THRESHOLD      = 1.20
    SPEND_UNDERPACE_THRESHOLD     = 0.20
    SPEND_CONCENTRATION_THRESHOLD = 0.80
    CTR_DROP_THRESHOLD            = 0.30
    IS_DROP_THRESHOLD             = 15.0
    CPC_SPIKE_THRESHOLD           = 0.40
    ZERO_IMPRESSION_DAYS          = 7
    MIN_ACCOUNT_SPEND_30D         = 50.0
    MAX_ZERO_IMPRESSION_ALERTS    = 5
    CLIENT_OVERRIDES              = {}

# ─── GOOGLE ADS CLIENT ───────────────────────────────────────────────────────

def build_client():
    return GoogleAdsClient.load_from_dict({
        "developer_token":   os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
        "client_id":         os.environ["GOOGLE_ADS_CLIENT_ID"],
        "client_secret":     os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        "refresh_token":     os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
        "login_customer_id": os.environ["GOOGLE_ADS_CUSTOMER_ID"],
        "use_proto_plus":    True,
    })


def run_query(ga_service, customer_id, query):
    try:
        return list(ga_service.search(customer_id=customer_id, query=query))
    except GoogleAdsException as ex:
        for error in ex.failure.errors:
            print(f"    [API Error] {error.message}", file=sys.stderr)
        return []


# ─── DATE HELPERS ─────────────────────────────────────────────────────────────

def get_date_ranges():
    today     = date.today()
    yesterday = today - timedelta(days=1)
    return {
        "today":            today.strftime("%Y-%m-%d"),
        "yesterday":        yesterday.strftime("%Y-%m-%d"),
        "this_week_start":  (today - timedelta(days=7)).strftime("%Y-%m-%d"),
        "this_week_end":    yesterday.strftime("%Y-%m-%d"),
        "prior_week_start": (today - timedelta(days=14)).strftime("%Y-%m-%d"),
        "prior_week_end":   (today - timedelta(days=8)).strftime("%Y-%m-%d"),
    }


# ─── CHECKS ──────────────────────────────────────────────────────────────────

def check_conversions(ga_service, customer_id, dates, overrides):
    """
    Compares yesterday's conversions against a 7-day rolling daily average.
    Flags: zero conversions on normally-converting accounts, >50% drops.
    """
    min_avg    = overrides.get("CONV_ZERO_MIN_DAILY_AVG", CONV_ZERO_MIN_DAILY_AVG)
    drop_thresh = overrides.get("CONV_DROP_THRESHOLD", CONV_DROP_THRESHOLD)

    rows = run_query(ga_service, customer_id, f"""
        SELECT
            segments.date,
            metrics.conversions
        FROM customer
        WHERE segments.date >= '{dates["this_week_start"]}'
          AND segments.date <= '{dates["this_week_end"]}'
    """)

    daily = defaultdict(float)
    for row in rows:
        daily[row.segments.date] += row.metrics.conversions

    if not daily:
        return []

    daily_avg       = sum(daily.values()) / len(daily)
    yesterday_conv  = daily.get(dates["yesterday"], 0.0)

    issues = []

    if daily_avg >= min_avg:
        if yesterday_conv == 0:
            issues.append({
                "level":   "CRITICAL",
                "message": f"0 conversions yesterday (7-day avg: {daily_avg:.1f}/day). "
                           f"Possible tag breakage or all campaigns stopped.",
            })
        else:
            drop_ratio = (daily_avg - yesterday_conv) / daily_avg
            if drop_ratio >= drop_thresh:
                issues.append({
                    "level":   "CRITICAL",
                    "message": f"Conversions down {drop_ratio*100:.0f}% yesterday "
                               f"({yesterday_conv:.0f} vs {daily_avg:.1f}/day avg). "
                               f"Check conversion tracking and campaign status.",
                })

    return issues


def check_spend(ga_service, customer_id, dates):
    """
    Flags budget overpacing, underpacing, and single-campaign concentration risk.
    Uses yesterday's full-day spend vs daily budgets.
    """
    rows = run_query(ga_service, customer_id, f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign_budget.amount_micros,
            metrics.cost_micros
        FROM campaign
        WHERE segments.date = '{dates["yesterday"]}'
          AND campaign.status = ENABLED
        ORDER BY metrics.cost_micros DESC
    """)

    issues   = []
    budgets  = []

    for row in rows:
        daily_budget = row.campaign_budget.amount_micros / 1_000_000
        actual_spend = row.metrics.cost_micros / 1_000_000
        if daily_budget > 0:
            budgets.append((row.campaign.name, daily_budget, actual_spend))

    if not budgets:
        return issues

    total_budget = sum(b for _, b, _ in budgets)
    total_spend  = sum(s for _, _, s in budgets)

    if total_budget > 0:
        ratio = total_spend / total_budget
        if ratio > SPEND_OVERPACE_THRESHOLD:
            issues.append({
                "level":   "WARNING",
                "message": f"Account overpaced yesterday: spent ${total_spend:.2f} vs "
                           f"${total_budget:.2f} budget ({ratio*100:.0f}%). "
                           f"Check for bid strategy anomalies.",
            })
        elif ratio < SPEND_UNDERPACE_THRESHOLD:
            issues.append({
                "level":   "WARNING",
                "message": f"Account underpaced yesterday: spent ${total_spend:.2f} vs "
                           f"${total_budget:.2f} budget ({ratio*100:.0f}%). "
                           f"Campaigns may have stopped or budgets are unspendable.",
            })

    if total_spend > 0 and len(budgets) > 1:
        top_name, _, top_spend = max(budgets, key=lambda x: x[2])
        concentration = top_spend / total_spend
        if concentration >= SPEND_CONCENTRATION_THRESHOLD:
            issues.append({
                "level":   "WARNING",
                "message": f"Budget concentration: '{top_name}' consumed "
                           f"{concentration*100:.0f}% of account spend "
                           f"(${top_spend:.2f} of ${total_spend:.2f}).",
            })

    return issues


def check_traffic_quality(ga_service, customer_id, dates):
    """
    WoW comparison of CTR, Search Impression Share, and avg CPC.
    Uses account-level aggregates for current and prior 7-day windows.
    """

    def get_metrics(start, end):
        rows = run_query(ga_service, customer_id, f"""
            SELECT
                metrics.clicks,
                metrics.impressions,
                metrics.cost_micros,
                metrics.search_impression_share
            FROM customer
            WHERE segments.date >= '{start}'
              AND segments.date <= '{end}'
        """)
        clicks = 0; impressions = 0; cost = 0.0; is_vals = []
        for row in rows:
            clicks      += row.metrics.clicks
            impressions += row.metrics.impressions
            cost        += row.metrics.cost_micros / 1_000_000
            if row.metrics.search_impression_share > 0:
                is_vals.append(row.metrics.search_impression_share)
        ctr     = clicks / impressions if impressions > 0 else 0.0
        avg_cpc = cost / clicks if clicks > 0 else 0.0
        avg_is  = sum(is_vals) / len(is_vals) if is_vals else 0.0
        return ctr, avg_cpc, avg_is

    this_ctr, this_cpc, this_is = get_metrics(dates["this_week_start"],  dates["this_week_end"])
    prev_ctr, prev_cpc, prev_is = get_metrics(dates["prior_week_start"], dates["prior_week_end"])

    issues = []

    if prev_ctr > 0:
        ctr_drop = (prev_ctr - this_ctr) / prev_ctr
        if ctr_drop >= CTR_DROP_THRESHOLD:
            issues.append({
                "level":   "WARNING",
                "message": f"CTR dropped {ctr_drop*100:.0f}% WoW "
                           f"({prev_ctr*100:.2f}% to {this_ctr*100:.2f}%). "
                           f"Check ad relevance, Quality Score, and search term shifts.",
            })

    if prev_is > 0:
        is_drop = (prev_is - this_is) * 100   # convert to percentage points
        if is_drop >= IS_DROP_THRESHOLD:
            issues.append({
                "level":   "WARNING",
                "message": f"Search Impression Share dropped {is_drop:.1f} points WoW "
                           f"({prev_is*100:.1f}% to {this_is*100:.1f}%). "
                           f"Check budgets and competitor activity.",
            })

    if prev_cpc > 0:
        cpc_spike = (this_cpc - prev_cpc) / prev_cpc
        if cpc_spike >= CPC_SPIKE_THRESHOLD:
            issues.append({
                "level":   "WARNING",
                "message": f"Avg CPC up {cpc_spike*100:.0f}% WoW "
                           f"(${prev_cpc:.2f} to ${this_cpc:.2f}). "
                           f"Check competitor bid increases and Quality Score.",
            })

    return issues


def check_disapprovals(ga_service, customer_id):
    """Flags disapproved ads in active campaigns and ad groups."""
    rows = run_query(ga_service, customer_id, """
        SELECT
            campaign.name,
            campaign.status,
            ad_group.name,
            ad_group.status,
            ad_group_ad.ad.id,
            ad_group_ad.policy_summary.approval_status,
            ad_group_ad.policy_summary.policy_topic_entries
        FROM ad_group_ad
        WHERE ad_group_ad.status = ENABLED
          AND ad_group_ad.policy_summary.approval_status = DISAPPROVED
    """)

    issues = []
    for row in rows:
        campaign_active  = row.campaign.status.name  == "ENABLED"
        ad_group_active  = row.ad_group.status.name  == "ENABLED"
        if not (campaign_active and ad_group_active):
            continue

        topics = [t.topic for t in row.ad_group_ad.policy_summary.policy_topic_entries] \
                 if row.ad_group_ad.policy_summary.policy_topic_entries else []
        topic_str = ", ".join(topics) if topics else "no topic detail"

        issues.append({
            "level":   "CRITICAL",
            "message": f"Ad DISAPPROVED in [{row.campaign.name}] / [{row.ad_group.name}] "
                       f"— {topic_str}.",
        })

    return issues


def check_zero_impression_ad_groups(ga_service, customer_id, dates):
    """
    Flags active ad groups with zero impressions over the last 7 days.
    Capped at MAX_ZERO_IMPRESSION_ALERTS to prevent flooding.
    """
    rows = run_query(ga_service, customer_id, f"""
        SELECT
            campaign.name,
            campaign.status,
            ad_group.name,
            ad_group.status,
            metrics.impressions
        FROM ad_group
        WHERE ad_group.status   = ENABLED
          AND campaign.status   = ENABLED
          AND segments.date    >= '{dates["this_week_start"]}'
          AND segments.date    <= '{dates["this_week_end"]}'
    """)

    ag_impressions = defaultdict(lambda: {"campaign": "", "impressions": 0})
    for row in rows:
        key = f"{row.campaign.name}|||{row.ad_group.name}"
        ag_impressions[key]["campaign"]    = row.campaign.name
        ag_impressions[key]["impressions"] += row.metrics.impressions

    issues = []
    for key, data in ag_impressions.items():
        if data["impressions"] == 0:
            ag_name = key.split("|||", 1)[1]
            issues.append({
                "level":   "WARNING",
                "message": f"Ad group [{ag_name}] in [{data['campaign']}] — "
                           f"0 impressions in last 7 days. "
                           f"Check keywords, bids, Quality Scores, and ad status.",
            })

    if len(issues) > MAX_ZERO_IMPRESSION_ALERTS:
        count  = len(issues)
        issues = issues[:MAX_ZERO_IMPRESSION_ALERTS]
        issues.append({
            "level":   "WARNING",
            "message": f"... and {count - MAX_ZERO_IMPRESSION_ALERTS} more ad groups "
                       f"with 0 impressions (truncated). Review account structure.",
        })

    return issues


# ─── AUDIT ONE ACCOUNT ────────────────────────────────────────────────────────

def audit_account(ga_service, customer_id, client_name, dates):
    """Run all anomaly checks for one account and return structured results."""
    overrides = CLIENT_OVERRIDES.get(customer_id, {})

    all_issues = []
    all_issues += check_conversions(ga_service, customer_id, dates, overrides)
    all_issues += check_spend(ga_service, customer_id, dates)
    all_issues += check_traffic_quality(ga_service, customer_id, dates)
    all_issues += check_disapprovals(ga_service, customer_id)
    all_issues += check_zero_impression_ad_groups(ga_service, customer_id, dates)

    critical = [i for i in all_issues if i["level"] == "CRITICAL"]
    warnings = [i for i in all_issues if i["level"] == "WARNING"]

    return {
        "client_name": client_name,
        "customer_id": customer_id,
        "critical":    critical,
        "warnings":    warnings,
        "all_clear":   not critical and not warnings,
        "error":       None,
    }


# ─── REPORT BUILDER ──────────────────────────────────────────────────────────

def build_report(results, run_date):
    """Build the formatted anomaly report string."""
    critical_clients = [r for r in results if r["critical"] and not r.get("error")]
    warning_clients  = [r for r in results if not r["critical"] and r["warnings"] and not r.get("error")]
    clear_clients    = [r for r in results if r["all_clear"] and not r.get("error")]
    errored_clients  = [r for r in results if r.get("error")]

    lines = [
        f"ANOMALY REPORT — {run_date}",
        "=" * 70,
        "",
    ]

    if critical_clients:
        lines.append("CRITICAL")
        lines.append("-" * 30)
        for r in critical_clients:
            lines.append(f"  {r['client_name']} ({r['customer_id']})")
            for issue in r["critical"]:
                lines.append(f"    - {issue['message']}")
            for issue in r["warnings"]:
                lines.append(f"    - [warn] {issue['message']}")
        lines.append("")

    if warning_clients:
        lines.append("WARNING")
        lines.append("-" * 30)
        for r in warning_clients:
            lines.append(f"  {r['client_name']} ({r['customer_id']})")
            for issue in r["warnings"]:
                lines.append(f"    - {issue['message']}")
        lines.append("")

    if clear_clients:
        names = ", ".join(r["client_name"] for r in clear_clients)
        lines.append(f"ALL CLEAR: {names}")
        lines.append("")

    if errored_clients:
        lines.append("ERRORS (could not check):")
        for r in errored_clients:
            lines.append(f"  {r['client_name']} ({r['customer_id']}): {r['error']}")
        lines.append("")

    lines += [
        "=" * 70,
        f"  Total accounts:   {len(results)}",
        f"  Critical issues:  {len(critical_clients)}",
        f"  Warnings:         {len(warning_clients)}",
        f"  All clear:        {len(clear_clients)}",
        "=" * 70,
    ]

    return "\n".join(lines)


def save_report(text, run_date):
    """Save the report to reports/anomaly-YYYY-MM-DD.md in the project root."""
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    path = reports_dir / f"anomaly-{run_date}.md"
    path.write_text(text, encoding="utf-8")
    return path


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Anomaly monitor — daily scan of all client accounts"
    )
    parser.add_argument("--customer-id",  help="Single account ID (omit for all clients)")
    parser.add_argument("--client-name",  help="Display name when using --customer-id")
    parser.add_argument("--save",         action="store_true",
                        help="Save report to reports/anomaly-YYYY-MM-DD.md")
    args = parser.parse_args()

    run_date = date.today().strftime("%Y-%m-%d")
    dates    = get_date_ranges()

    client     = build_client()
    ga_service = client.get_service("GoogleAdsService")

    if args.customer_id:
        targets = {(args.client_name or args.customer_id): args.customer_id.replace("-", "")}
    else:
        targets = ALL_CLIENTS

    print("\n" + "=" * 70)
    print(f"ANOMALY MONITOR — {run_date}")
    print(f"Scanning {len(targets)} account(s) ...")
    print("=" * 70)

    results = []
    for name, cid in targets.items():
        try:
            result = audit_account(ga_service, cid, name, dates)
            results.append(result)

            if result["critical"]:
                icon = "CRITICAL"
            elif result["warnings"]:
                icon = "WARNING "
            else:
                icon = "OK      "
            print(f"  [{icon}]  {name}")

        except Exception as e:
            results.append({
                "client_name": name,
                "customer_id": cid,
                "critical":    [],
                "warnings":    [],
                "all_clear":   False,
                "error":       str(e),
            })
            print(f"  [ERROR  ]  {name} — {e}")

    report_text = build_report(results, run_date)
    print("\n" + report_text)

    if args.save:
        path = save_report(report_text, run_date)
        print(f"\n  Saved: {path}")


if __name__ == "__main__":
    main()
