"""
Full Campaign Audit Script
Purpose: Pull comprehensive performance data for any Google Ads client account.
         Covers: Campaign Performance, Ad Groups, Conversions, Search Terms,
                 Keywords (with Quality Score), Ad Copies, Asset Performance,
                 Negative Keywords, and Monthly Trends.

Setup:
    Requires environment variables:
        GOOGLE_ADS_DEVELOPER_TOKEN
        GOOGLE_ADS_CLIENT_ID
        GOOGLE_ADS_CLIENT_SECRET
        GOOGLE_ADS_REFRESH_TOKEN
        GOOGLE_ADS_CUSTOMER_ID  (your MCC ID)

Usage:
    python3 scripts/full_audit.py --customer-id 5216656756
    python3 scripts/full_audit.py --customer-id 5216656756 --days 30
    python3 scripts/full_audit.py --customer-id 5216656756 --days 90 --client-name "Voit Dental"

Changelog:
    2026-03-18  Initial version (extracted from voit_dental_full_audit.py, made generic)
"""

import argparse
import os
from datetime import datetime, timedelta

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# ─── ARGS ────────────────────────────────────────────────────────────────────

parser = argparse.ArgumentParser(description="Full Google Ads account audit")
parser.add_argument("--customer-id", required=True, help="Google Ads account ID (no dashes)")
parser.add_argument("--days", type=int, default=60, help="Lookback window in days (default: 60)")
parser.add_argument("--client-name", default="", help="Optional display name for output headers")
args = parser.parse_args()

CUSTOMER_ID = args.customer_id.replace("-", "")
DAYS = args.days
CLIENT_LABEL = args.client_name or CUSTOMER_ID

date_end = datetime.today().date()
date_start = date_end - timedelta(days=DAYS - 1)
DATE_RANGE = f"BETWEEN '{date_start}' AND '{date_end}'"

# ─── CLIENT ──────────────────────────────────────────────────────────────────

client = GoogleAdsClient.load_from_dict({
    "developer_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
    "client_id": os.environ["GOOGLE_ADS_CLIENT_ID"],
    "client_secret": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
    "refresh_token": os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
    "login_customer_id": os.environ["GOOGLE_ADS_CUSTOMER_ID"],
    "use_proto_plus": True
})

ga_service = client.get_service("GoogleAdsService")


def run_query(query):
    try:
        response = ga_service.search(customer_id=CUSTOMER_ID, query=query)
        return list(response)
    except GoogleAdsException as ex:
        print(f"Query failed: {ex}")
        return []


print("\n" + "="*60)
print(f"AUDIT: {CLIENT_LABEL} (Account: {CUSTOMER_ID})")
print(f"Period: {date_start} to {date_end} ({DAYS} days)")
print("="*60)

# ─── 1. CAMPAIGN PERFORMANCE ────────────────────────────────────────────────
print("\n" + "="*60)
print("1. CAMPAIGN PERFORMANCE")
print("="*60)

rows = run_query(f"""
    SELECT
        campaign.id,
        campaign.name,
        campaign.status,
        campaign.advertising_channel_type,
        campaign.bidding_strategy_type,
        campaign_budget.amount_micros,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.conversions_value,
        metrics.ctr,
        metrics.average_cpc,
        metrics.search_impression_share,
        metrics.search_top_impression_share,
        metrics.search_absolute_top_impression_share
    FROM campaign
    WHERE segments.date {DATE_RANGE}
    ORDER BY metrics.cost_micros DESC
""")

campaigns = {}
for row in rows:
    c = row.campaign
    m = row.metrics
    b = row.campaign_budget
    cid = str(c.id)
    if cid not in campaigns:
        campaigns[cid] = {
            "id": cid,
            "name": c.name,
            "status": c.status.name,
            "type": c.advertising_channel_type.name,
            "bidding": c.bidding_strategy_type.name,
            "budget_daily": b.amount_micros / 1_000_000,
            "impressions": 0, "clicks": 0, "cost": 0,
            "conversions": 0, "conv_value": 0
        }
    campaigns[cid]["impressions"] += m.impressions
    campaigns[cid]["clicks"] += m.clicks
    campaigns[cid]["cost"] += m.cost_micros / 1_000_000
    campaigns[cid]["conversions"] += m.conversions
    campaigns[cid]["conv_value"] += m.conversions_value

for cid, c in campaigns.items():
    ctr = (c["clicks"] / c["impressions"] * 100) if c["impressions"] > 0 else 0
    cpc = (c["cost"] / c["clicks"]) if c["clicks"] > 0 else 0
    cpa = (c["cost"] / c["conversions"]) if c["conversions"] > 0 else 0
    cvr = (c["conversions"] / c["clicks"] * 100) if c["clicks"] > 0 else 0
    print(f"\nCampaign: {c['name']} [{c['status']}]")
    print(f"  ID: {cid} | Type: {c['type']} | Bidding: {c['bidding']}")
    print(f"  Daily Budget: ${c['budget_daily']:.2f}")
    print(f"  Impressions: {c['impressions']:,} | Clicks: {c['clicks']:,} | CTR: {ctr:.2f}%")
    print(f"  Cost: ${c['cost']:.2f} | Avg CPC: ${cpc:.2f}")
    print(f"  Conversions: {c['conversions']:.1f} | CVR: {cvr:.2f}% | CPA: ${cpa:.2f}")

# ─── 2. AD GROUP PERFORMANCE ────────────────────────────────────────────────
print("\n" + "="*60)
print("2. AD GROUP PERFORMANCE")
print("="*60)

rows = run_query(f"""
    SELECT
        campaign.name,
        ad_group.id,
        ad_group.name,
        ad_group.status,
        ad_group.type,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.ctr,
        metrics.average_cpc
    FROM ad_group
    WHERE segments.date {DATE_RANGE}
    ORDER BY campaign.name, metrics.cost_micros DESC
""")

ad_groups = {}
for row in rows:
    ag = row.ad_group
    m = row.metrics
    agid = str(ag.id)
    if agid not in ad_groups:
        ad_groups[agid] = {
            "campaign": row.campaign.name,
            "name": ag.name,
            "status": ag.status.name,
            "type": ag.type_.name,
            "impressions": 0, "clicks": 0, "cost": 0, "conversions": 0
        }
    ad_groups[agid]["impressions"] += m.impressions
    ad_groups[agid]["clicks"] += m.clicks
    ad_groups[agid]["cost"] += m.cost_micros / 1_000_000
    ad_groups[agid]["conversions"] += m.conversions

for agid, ag in ad_groups.items():
    ctr = (ag["clicks"] / ag["impressions"] * 100) if ag["impressions"] > 0 else 0
    cpc = (ag["cost"] / ag["clicks"]) if ag["clicks"] > 0 else 0
    cvr = (ag["conversions"] / ag["clicks"] * 100) if ag["clicks"] > 0 else 0
    print(f"\n  [{ag['campaign']}] {ag['name']} [{ag['status']}]")
    print(f"    Impr: {ag['impressions']:,} | Clicks: {ag['clicks']:,} | CTR: {ctr:.2f}%")
    print(f"    Cost: ${ag['cost']:.2f} | CPC: ${cpc:.2f} | Conv: {ag['conversions']:.1f} | CVR: {cvr:.2f}%")

# ─── 3. CONVERSION ACTIONS ──────────────────────────────────────────────────
print("\n" + "="*60)
print("3. CONVERSIONS BY ACTION TYPE")
print("="*60)

rows = run_query(f"""
    SELECT
        campaign.name,
        conversion_action.name,
        conversion_action.category,
        conversion_action.type,
        metrics.conversions,
        metrics.conversions_value,
        metrics.all_conversions,
        metrics.view_through_conversions
    FROM campaign
    WHERE segments.date {DATE_RANGE}
      AND metrics.all_conversions > 0
    ORDER BY campaign.name, metrics.all_conversions DESC
""")

if rows:
    for row in rows:
        ca = row.conversion_action
        m = row.metrics
        print(f"\n  Campaign: {row.campaign.name}")
        print(f"    Action: {ca.name} | Category: {ca.category.name} | Type: {ca.type_.name}")
        print(f"    Conversions: {m.conversions:.1f} | All Conv: {m.all_conversions:.1f} | View-through: {m.view_through_conversions:.1f}")
else:
    # Fallback: segment by conversion action name
    rows2 = run_query(f"""
        SELECT
            campaign.name,
            segments.conversion_action_name,
            segments.conversion_action_category,
            metrics.conversions,
            metrics.all_conversions
        FROM campaign
        WHERE segments.date {DATE_RANGE}
        ORDER BY campaign.name, metrics.all_conversions DESC
    """)
    for row in rows2:
        if row.metrics.all_conversions > 0:
            print(f"\n  Campaign: {row.campaign.name}")
            print(f"    Action: {row.segments.conversion_action_name}")
            print(f"    Category: {row.segments.conversion_action_category.name}")
            print(f"    Conv: {row.metrics.conversions:.1f} | All Conv: {row.metrics.all_conversions:.1f}")

# ─── 4. SEARCH TERMS ────────────────────────────────────────────────────────
print("\n" + "="*60)
print("4. SEARCH TERMS REPORT")
print("="*60)

rows = run_query(f"""
    SELECT
        campaign.name,
        ad_group.name,
        search_term_view.search_term,
        search_term_view.status,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.ctr,
        metrics.average_cpc
    FROM search_term_view
    WHERE segments.date {DATE_RANGE}
    ORDER BY metrics.clicks DESC
    LIMIT 200
""")

print(f"\nTotal search terms found: {len(rows)}")
print("\nTop Search Terms by Clicks:")
for i, row in enumerate(rows[:50]):
    st = row.search_term_view
    m = row.metrics
    cost = m.cost_micros / 1_000_000
    print(f"  {i+1:3}. [{st.status.name}] \"{st.search_term}\"")
    print(f"       Campaign: {row.campaign.name} | AdGroup: {row.ad_group.name}")
    print(f"       Impr: {m.impressions:,} | Clicks: {m.clicks:,} | CTR: {m.ctr*100:.2f}% | Cost: ${cost:.2f} | CPC: ${m.average_cpc/1_000_000:.2f} | Conv: {m.conversions:.1f}")

print("\nTop Converting Search Terms:")
conv_terms = sorted(rows, key=lambda r: r.metrics.conversions, reverse=True)
for i, row in enumerate(conv_terms[:20]):
    if row.metrics.conversions > 0:
        st = row.search_term_view
        m = row.metrics
        cost = m.cost_micros / 1_000_000
        cpa = cost / m.conversions if m.conversions > 0 else 0
        print(f"  {i+1:2}. \"{st.search_term}\" → Conv: {m.conversions:.1f} | CPA: ${cpa:.2f} | Clicks: {m.clicks}")

# ─── 5. TARGET KEYWORDS ─────────────────────────────────────────────────────
print("\n" + "="*60)
print("5. TARGET KEYWORDS")
print("="*60)

rows = run_query(f"""
    SELECT
        campaign.name,
        ad_group.name,
        ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type,
        ad_group_criterion.status,
        ad_group_criterion.final_urls,
        ad_group_criterion.quality_info.quality_score,
        ad_group_criterion.quality_info.creative_quality_score,
        ad_group_criterion.quality_info.post_click_quality_score,
        ad_group_criterion.quality_info.search_predicted_ctr,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.ctr,
        metrics.average_cpc,
        metrics.search_impression_share,
        metrics.search_top_impression_share
    FROM keyword_view
    WHERE segments.date {DATE_RANGE}
    ORDER BY metrics.cost_micros DESC
""")

print(f"\nTotal keywords: {len(rows)}")
keywords_data = {}
for row in rows:
    kw = row.ad_group_criterion
    m = row.metrics
    key = f"{kw.keyword.text}|{kw.keyword.match_type.name}"
    if key not in keywords_data:
        keywords_data[key] = {
            "text": kw.keyword.text,
            "match_type": kw.keyword.match_type.name,
            "status": kw.status.name,
            "campaign": row.campaign.name,
            "ad_group": row.ad_group.name,
            "quality_score": kw.quality_info.quality_score,
            "creative_quality": kw.quality_info.creative_quality_score.name if kw.quality_info.creative_quality_score else "N/A",
            "landing_quality": kw.quality_info.post_click_quality_score.name if kw.quality_info.post_click_quality_score else "N/A",
            "predicted_ctr": kw.quality_info.search_predicted_ctr.name if kw.quality_info.search_predicted_ctr else "N/A",
            "impressions": 0, "clicks": 0, "cost": 0, "conversions": 0
        }
    keywords_data[key]["impressions"] += m.impressions
    keywords_data[key]["clicks"] += m.clicks
    keywords_data[key]["cost"] += m.cost_micros / 1_000_000
    keywords_data[key]["conversions"] += m.conversions

print("\nAll Keywords:")
for key, kw in sorted(keywords_data.items(), key=lambda x: x[1]["cost"], reverse=True):
    ctr = (kw["clicks"] / kw["impressions"] * 100) if kw["impressions"] > 0 else 0
    cpc = (kw["cost"] / kw["clicks"]) if kw["clicks"] > 0 else 0
    cpa = (kw["cost"] / kw["conversions"]) if kw["conversions"] > 0 else 0
    print(f"\n  [{kw['status']}] \"{kw['text']}\" [{kw['match_type']}]")
    print(f"    Campaign: {kw['campaign']} | AdGroup: {kw['ad_group']}")
    print(f"    QS: {kw['quality_score']} | Creative: {kw['creative_quality']} | Landing: {kw['landing_quality']} | pCTR: {kw['predicted_ctr']}")
    print(f"    Impr: {kw['impressions']:,} | Clicks: {kw['clicks']:,} | CTR: {ctr:.2f}% | Cost: ${kw['cost']:.2f} | CPC: ${cpc:.2f} | Conv: {kw['conversions']:.1f} | CPA: ${cpa:.2f}")

# ─── 6. AD COPIES ───────────────────────────────────────────────────────────
print("\n" + "="*60)
print("6. AD COPIES - RESPONSIVE SEARCH ADS")
print("="*60)

rows = run_query(f"""
    SELECT
        campaign.name,
        ad_group.name,
        ad_group_ad.ad.id,
        ad_group_ad.status,
        ad_group_ad.ad.final_urls,
        ad_group_ad.ad.responsive_search_ad.headlines,
        ad_group_ad.ad.responsive_search_ad.descriptions,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.ctr,
        metrics.average_cpc
    FROM ad_group_ad
    WHERE segments.date {DATE_RANGE}
      AND ad_group_ad.ad.type = RESPONSIVE_SEARCH_AD
    ORDER BY metrics.impressions DESC
""")

print(f"\nTotal RSAs found: {len(rows)}")
ads_data = {}
for row in rows:
    ad = row.ad_group_ad
    m = row.metrics
    ad_id = str(ad.ad.id)
    if ad_id not in ads_data:
        rsa = ad.ad.responsive_search_ad
        ads_data[ad_id] = {
            "campaign": row.campaign.name,
            "ad_group": row.ad_group.name,
            "status": ad.status.name,
            "final_urls": list(ad.ad.final_urls),
            "headlines": [h.text for h in rsa.headlines] if rsa.headlines else [],
            "descriptions": [d.text for d in rsa.descriptions] if rsa.descriptions else [],
            "impressions": 0, "clicks": 0, "cost": 0, "conversions": 0
        }
    ads_data[ad_id]["impressions"] += m.impressions
    ads_data[ad_id]["clicks"] += m.clicks
    ads_data[ad_id]["cost"] += m.cost_micros / 1_000_000
    ads_data[ad_id]["conversions"] += m.conversions

for ad_id, ad in sorted(ads_data.items(), key=lambda x: x[1]["impressions"], reverse=True):
    ctr = (ad["clicks"] / ad["impressions"] * 100) if ad["impressions"] > 0 else 0
    cpc = (ad["cost"] / ad["clicks"]) if ad["clicks"] > 0 else 0
    cpa = (ad["cost"] / ad["conversions"]) if ad["conversions"] > 0 else 0
    print(f"\n  [{ad['status']}] Campaign: {ad['campaign']} | AdGroup: {ad['ad_group']}")
    print(f"  Final URL: {ad['final_urls']}")
    print(f"  Impr: {ad['impressions']:,} | Clicks: {ad['clicks']:,} | CTR: {ctr:.2f}% | Cost: ${ad['cost']:.2f} | CPC: ${cpc:.2f} | Conv: {ad['conversions']:.1f} | CPA: ${cpa:.2f}")
    print(f"  HEADLINES ({len(ad['headlines'])}):")
    for i, h in enumerate(ad["headlines"], 1):
        print(f"    H{i}: {h}")
    print(f"  DESCRIPTIONS ({len(ad['descriptions'])}):")
    for i, d in enumerate(ad["descriptions"], 1):
        print(f"    D{i}: {d}")

# ─── 7. AD ASSET PERFORMANCE ────────────────────────────────────────────────
print("\n" + "="*60)
print("7. AD ASSET PERFORMANCE (Headline/Description level)")
print("="*60)

rows = run_query(f"""
    SELECT
        campaign.name,
        ad_group.name,
        ad_group_ad.ad.id,
        asset.text_asset.text,
        asset.field_type,
        ad_group_ad_asset_view.performance_label,
        ad_group_ad_asset_view.enabled,
        metrics.impressions
    FROM ad_group_ad_asset_view
    WHERE segments.date {DATE_RANGE}
      AND asset.type = TEXT
    ORDER BY campaign.name, metrics.impressions DESC
""")

print(f"\nTotal assets found: {len(rows)}")
for row in rows:
    asset = row.asset
    av = row.ad_group_ad_asset_view
    print(f"  [{row.campaign.name}] [{row.ad_group.name}] [{asset.field_type.name}] \"{asset.text_asset.text}\"")
    print(f"    Performance: {av.performance_label.name} | Enabled: {av.enabled} | Impr: {row.metrics.impressions:,}")

# ─── 8. NEGATIVE KEYWORDS ───────────────────────────────────────────────────
print("\n" + "="*60)
print("8. NEGATIVE KEYWORDS")
print("="*60)

campaign_negs = run_query("""
    SELECT
        campaign.name,
        campaign_criterion.keyword.text,
        campaign_criterion.keyword.match_type,
        campaign_criterion.negative
    FROM campaign_criterion
    WHERE campaign_criterion.negative = TRUE
      AND campaign_criterion.type = KEYWORD
    ORDER BY campaign.name
""")

adgroup_negs = run_query("""
    SELECT
        campaign.name,
        ad_group.name,
        ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type,
        ad_group_criterion.negative
    FROM ad_group_criterion
    WHERE ad_group_criterion.negative = TRUE
      AND ad_group_criterion.type = KEYWORD
    ORDER BY campaign.name, ad_group.name
""")

print(f"\nCampaign-level negatives: {len(campaign_negs)}")
for row in campaign_negs:
    kw = row.campaign_criterion.keyword
    print(f"  [{row.campaign.name}] -{kw.text} [{kw.match_type.name}]")

print(f"\nAd Group-level negatives: {len(adgroup_negs)}")
for row in adgroup_negs:
    kw = row.ad_group_criterion.keyword
    print(f"  [{row.campaign.name}] [{row.ad_group.name}] -{kw.text} [{kw.match_type.name}]")

# ─── 9. MONTHLY TREND ───────────────────────────────────────────────────────
print("\n" + "="*60)
print("9. MONTHLY PERFORMANCE TREND")
print("="*60)

rows = run_query(f"""
    SELECT
        campaign.name,
        segments.month,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.ctr,
        metrics.average_cpc
    FROM campaign
    WHERE segments.date {DATE_RANGE}
    ORDER BY campaign.name, segments.month
""")

monthly = {}
for row in rows:
    key = f"{row.campaign.name}|{row.segments.month}"
    if key not in monthly:
        monthly[key] = {"campaign": row.campaign.name, "month": row.segments.month,
                        "impressions": 0, "clicks": 0, "cost": 0, "conversions": 0}
    monthly[key]["impressions"] += row.metrics.impressions
    monthly[key]["clicks"] += row.metrics.clicks
    monthly[key]["cost"] += row.metrics.cost_micros / 1_000_000
    monthly[key]["conversions"] += row.metrics.conversions

for key, m in sorted(monthly.items()):
    ctr = (m["clicks"] / m["impressions"] * 100) if m["impressions"] > 0 else 0
    cpc = (m["cost"] / m["clicks"]) if m["clicks"] > 0 else 0
    cpa = (m["cost"] / m["conversions"]) if m["conversions"] > 0 else 0
    print(f"\n  {m['campaign']} | {m['month']}")
    print(f"    Impr: {m['impressions']:,} | Clicks: {m['clicks']:,} | CTR: {ctr:.2f}% | Cost: ${m['cost']:.2f} | CPC: ${cpc:.2f} | Conv: {m['conversions']:.1f} | CPA: ${cpa:.2f}")

print("\n" + "="*60)
print("DATA PULL COMPLETE")
print("="*60)
