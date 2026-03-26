"""
MCC Rollup
Purpose: Queries all 13 Google Ads client accounts in a single parallel pass
         via the MCC. Produces a ranked comparison table with WoW deltas for
         spend, conversions, CPA, CTR, and Search IS. Flags clients with >20%
         negative swings. Saves output to reports/mcc-rollup-YYYY-MM-DD.md.

         Run this on Monday morning before the weekly check to get an instant
         cross-client view.

Setup:
    Requires environment variables in .env:
        GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID,
        GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN,
        GOOGLE_ADS_CUSTOMER_ID  (MCC account ID: 4781259815)

Usage:
    python3 scripts/mcc_rollup.py                    # print table to terminal
    python3 scripts/mcc_rollup.py --save             # also save to reports/
    python3 scripts/mcc_rollup.py --threads 10       # increase parallelism

Output columns:
    Client | Spend | Conv | CPA | CTR | IS | Spend WoW | Conv WoW | CPA WoW | Alert

Changelog:
    2026-03-23  Initial version — parallel fetch via ThreadPoolExecutor,
                WoW delta table, >20% swing alerts, file output.
"""

import argparse
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
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

# Clients with >20% negative swing in spend, conversions, or CPA get an alert
SWING_ALERT_THRESHOLD = 0.20

# ─── GOOGLE ADS CLIENT ───────────────────────────────────────────────────────

def build_ga_client():
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
        # Suppress per-thread errors; caller handles None return
        return []


# ─── DATE HELPERS ─────────────────────────────────────────────────────────────

def get_date_ranges():
    """
    Returns the current and prior 7-day windows (both ending yesterday).
    Running on Monday gives Sun–Sat current week vs prior Sun–Sat.
    """
    today     = date.today()
    yesterday = today - timedelta(days=1)
    return {
        "this_start":  (today - timedelta(days=7)).strftime("%Y-%m-%d"),
        "this_end":    yesterday.strftime("%Y-%m-%d"),
        "prior_start": (today - timedelta(days=14)).strftime("%Y-%m-%d"),
        "prior_end":   (today - timedelta(days=8)).strftime("%Y-%m-%d"),
    }


# ─── PULL METRICS ─────────────────────────────────────────────────────────────

def pull_metrics(ga_service, customer_id, start_date, end_date):
    """Pull account-level summary for a date range."""
    rows = run_query(ga_service, customer_id, f"""
        SELECT
            metrics.clicks,
            metrics.impressions,
            metrics.cost_micros,
            metrics.conversions,
            metrics.search_impression_share
        FROM customer
        WHERE segments.date >= '{start_date}'
          AND segments.date <= '{end_date}'
    """)

    clicks = 0; impressions = 0; cost = 0.0; convs = 0.0; is_vals = []
    for row in rows:
        clicks      += row.metrics.clicks
        impressions += row.metrics.impressions
        cost        += row.metrics.cost_micros / 1_000_000
        convs       += row.metrics.conversions
        is_val       = row.metrics.search_impression_share
        if is_val and 0 < is_val <= 1:
            is_vals.append(is_val)

    ctr    = clicks / impressions if impressions > 0 else 0.0
    cpa    = cost / convs         if convs > 0        else 0.0
    avg_is = sum(is_vals) / len(is_vals) if is_vals  else 0.0

    return {
        "spend":  cost,
        "conv":   convs,
        "cpa":    cpa,
        "ctr":    ctr,
        "is":     avg_is,
        "clicks": clicks,
    }


def fetch_client_data(ga_client, client_name, customer_id, dr):
    """Fetch both periods for one client. Designed for ThreadPoolExecutor."""
    try:
        svc  = ga_client.get_service("GoogleAdsService")
        this = pull_metrics(svc, customer_id, dr["this_start"],  dr["this_end"])
        prev = pull_metrics(svc, customer_id, dr["prior_start"], dr["prior_end"])
        return {
            "client_name": client_name,
            "customer_id": customer_id,
            "this":        this,
            "prev":        prev,
            "error":       None,
        }
    except Exception as e:
        return {
            "client_name": client_name,
            "customer_id": customer_id,
            "this":        None,
            "prev":        None,
            "error":       str(e),
        }


# ─── DELTA HELPERS ────────────────────────────────────────────────────────────

def delta_pct(current, prior):
    """WoW change as a decimal fraction. None if prior is 0."""
    if not prior:
        return None
    return (current - prior) / prior


def fmt_delta(d, invert=False):
    """
    Format a delta for table display.
    invert=True: a decrease is GOOD (used for CPA — lower is better).
    """
    if d is None:
        return "  n/a  "
    arrow = "+" if d > 0 else "-"
    pct   = abs(d) * 100
    return f"{arrow}{pct:.0f}%"


def build_alerts(data):
    """Return a comma-separated alert string for clients with big negative swings."""
    t = data["this"]
    p = data["prev"]
    alerts = []

    sd = delta_pct(t["spend"], p["spend"])
    cd = delta_pct(t["conv"],  p["conv"])
    pd = delta_pct(t["cpa"],   p["cpa"])

    if sd is not None and sd < -SWING_ALERT_THRESHOLD:
        alerts.append(f"Spend -{abs(sd)*100:.0f}%")
    if cd is not None and cd < -SWING_ALERT_THRESHOLD:
        alerts.append(f"Conv -{abs(cd)*100:.0f}%")
    if pd is not None and pd > SWING_ALERT_THRESHOLD:
        alerts.append(f"CPA +{abs(pd)*100:.0f}%")

    return ", ".join(alerts) if alerts else ""


# ─── FORMAT TABLE ─────────────────────────────────────────────────────────────

COL_NAME   = 38
COL_SPEND  =  9
COL_CONV   =  6
COL_CPA    =  8
COL_CTR    =  6
COL_IS     =  6
COL_DELTA  =  8


def format_report(all_data, dr, run_date):
    """Build the ranked MCC rollup table."""
    valid   = sorted([d for d in all_data if not d["error"]],
                     key=lambda x: x["this"]["spend"], reverse=True)
    errored = [d for d in all_data if d["error"]]

    header = (
        f"{'Client':<{COL_NAME}} "
        f"{'Spend':>{COL_SPEND}} "
        f"{'Conv':>{COL_CONV}} "
        f"{'CPA':>{COL_CPA}} "
        f"{'CTR':>{COL_CTR}} "
        f"{'IS':>{COL_IS}}  "
        f"{'SpendWoW':>{COL_DELTA}} "
        f"{'ConvWoW':>{COL_DELTA}} "
        f"{'CPAWoW':>{COL_DELTA}}  Alert"
    )
    separator = "-" * len(header)

    lines = [
        f"MCC ROLLUP — Week {dr['this_start']} to {dr['this_end']}",
        f"Run date: {run_date}",
        "=" * len(header),
        "",
        header,
        separator,
    ]

    for d in valid:
        t      = d["this"]
        p      = d["prev"]
        alert  = build_alerts(d)
        flag   = "* " if alert else "  "

        name   = (flag + d["client_name"])[:COL_NAME]

        lines.append(
            f"{name:<{COL_NAME}} "
            f"${t['spend']:>{COL_SPEND-1},.0f} "
            f"{t['conv']:>{COL_CONV}.0f} "
            f"${t['cpa']:>{COL_CPA-1},.0f} "
            f"{t['ctr']*100:>{COL_CTR-1}.1f}% "
            f"{t['is']*100:>{COL_IS-1}.0f}%  "
            f"{fmt_delta(delta_pct(t['spend'], p['spend'])):>{COL_DELTA}} "
            f"{fmt_delta(delta_pct(t['conv'],  p['conv'])):>{COL_DELTA}} "
            f"{fmt_delta(delta_pct(t['cpa'],   p['cpa']), invert=True):>{COL_DELTA}}  "
            f"{alert}"
        )

    # Totals row
    if valid:
        ts = sum(d["this"]["spend"] for d in valid)
        tc = sum(d["this"]["conv"]  for d in valid)
        ps = sum(d["prev"]["spend"] for d in valid)
        pc = sum(d["prev"]["conv"]  for d in valid)
        ta = ts / tc if tc > 0 else 0
        pa = ps / pc if pc > 0 else 0

        lines.append(separator)
        lines.append(
            f"{'  TOTAL':<{COL_NAME}} "
            f"${ts:>{COL_SPEND-1},.0f} "
            f"{tc:>{COL_CONV}.0f} "
            f"${ta:>{COL_CPA-1},.0f} "
            f"{'':>{COL_CTR}} "
            f"{'':>{COL_IS}}  "
            f"{fmt_delta(delta_pct(ts, ps)):>{COL_DELTA}} "
            f"{fmt_delta(delta_pct(tc, pc)):>{COL_DELTA}} "
            f"{fmt_delta(delta_pct(ta, pa), invert=True):>{COL_DELTA}}"
        )

    lines.append("")
    lines.append(f"  * = client with >20% negative swing in spend, conversions, or CPA")

    if errored:
        lines.append("")
        lines.append("Could not fetch:")
        for d in errored:
            lines.append(f"  {d['client_name']} ({d['customer_id']}): {d['error']}")

    lines.append("")
    lines.append("=" * len(header))

    return "\n".join(lines)


def save_report(text, run_date):
    """Save the rollup to reports/mcc-rollup-YYYY-MM-DD.md."""
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    path = reports_dir / f"mcc-rollup-{run_date}.md"
    path.write_text(text, encoding="utf-8")
    return path


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="MCC rollup — cross-client weekly performance table"
    )
    parser.add_argument("--save",    action="store_true",
                        help="Save report to reports/mcc-rollup-YYYY-MM-DD.md")
    parser.add_argument("--threads", type=int, default=6,
                        help="Thread pool size for parallel queries (default: 6)")
    args = parser.parse_args()

    run_date = date.today().strftime("%Y-%m-%d")
    dr       = get_date_ranges()
    ga_client = build_ga_client()

    print(f"\nMCC ROLLUP — {run_date}")
    print(f"Querying {len(ALL_CLIENTS)} accounts in parallel (threads={args.threads}) ...")

    all_data = []
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {
            executor.submit(fetch_client_data, ga_client, name, cid, dr): name
            for name, cid in ALL_CLIENTS.items()
        }
        for future in as_completed(futures):
            result = future.result()
            ok     = "OK   " if not result["error"] else "ERROR"
            print(f"  [{ok}]  {result['client_name']}")
            all_data.append(result)

    report = format_report(all_data, dr, run_date)
    print("\n" + report)

    if args.save:
        path = save_report(report, run_date)
        print(f"  Saved: {path}")


if __name__ == "__main__":
    main()
