"""
Weekly Performance Report — All Clients
Purpose: Pulls the Sun-Sat weekly performance snapshot for every client
         across Google Ads and Meta Ads, then writes all rows to a single
         "Weekly Report" tab in Google Sheets.

Metrics per row:
    Week Start/End, Client, Platform, Status, Amount Spend,
    Form Leads, Call Leads, Blended Leads, Blended CPL, Closed Leads (manual),
    Online Purchase, Offline Purchase, Total Purchase, Purchase Value,
    Add to Carts, Checkouts, Total Revenue, ROAS,
    Top Performing Facebook Creative, Notes

Google Sheets ID: 1HYOZv1bbgIyNFQc2RoQqlkCL1a4viH8VkbSLe7xW-oY  (from .env)
Sheets Auth:      sheets-credentials.json (service account)

Usage:
    python3 scripts/weekly_performance_report.py                         # last Sun-Sat, all clients
    python3 scripts/weekly_performance_report.py --start 2026-03-15 --end 2026-03-21
    python3 scripts/weekly_performance_report.py --client "GDM"          # single client
    python3 scripts/weekly_performance_report.py --google-only
    python3 scripts/weekly_performance_report.py --meta-only
    python3 scripts/weekly_performance_report.py --no-creatives          # skip top-creative lookup (faster)
    python3 scripts/weekly_performance_report.py --replace               # overwrite this week's rows in sheet

Changelog:
    2026-03-22  Initial GDM-only version.
    2026-03-22  Expanded to all clients + Google Sheets output.
"""

import argparse
import os
import sys
from datetime import date, timedelta
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ─── CLIENT REGISTRY ──────────────────────────────────────────────────────────
# Add / remove clients here. Meta IDs without "act_" prefix are normalized below.

GOOGLE_CLIENTS = {
    "Anand Desai Law Firm":                 "5865660247",
    "Dentiste":                             "3857223862",
    "Estate Jewelry Priced Right":          "7709532223",
    "FaBesthetics":                         "9304117954",
    "GDM":                                  "7087867966",
    # Hoski.ca (5544702166) excluded — internal agency account, not a client
    "New Norseman":                         "3720173680",
    "Park Road Custom Furniture and Decor": "7228467515",
    "Serenity Familycare":                  "8134824884",
    "Synergy Spine & Nerve Center":         "7628667762",
    "Texas FHC":                            "8159668041",
    "Voit Dental 1":                        "5216656756",
}

META_CLIENTS = {
    "Bloomer Health":                       "215505746566668",
    "Estate Jewelry Priced Right":          "422065096974825",
    "GDM":                                  "1229672268157520",   # confirmed Mar 22 — ClickUp had wrong ID
    # ice Ad Account (1509969187799563) excluded — personal demo account, no ads_management permission
    "New Norseman":                         "1066181008711486",
    "Park Road Custom Furniture and Decor": "1302601091367185",
    "Serenity Familycare":                  "853944849499524",
    "Som K. Plastic Surgery":               "1401504290137519",
    "Sunstone Health":                      "4292269397710725",
    "Texas FHC":                            "331716185722452",
    "Voit Dental 1":                        "236091069101354",
}

MCC_ID = "4781259815"


def normalize_meta_id(raw_id: str) -> str:
    """Ensure Meta account IDs always carry the act_ prefix."""
    s = raw_id.strip()
    return s if s.startswith("act_") else f"act_{s}"


# ─── DATE RANGE ───────────────────────────────────────────────────────────────

def last_sun_sat_week(override_start=None, override_end=None):
    """Return (start_str, end_str) for the last completed Sun-Sat week."""
    if override_start and override_end:
        return override_start, override_end
    today = date.today()
    # Python weekday(): Mon=0 ... Sat=5, Sun=6
    # days_since_sat: how many days ago was last Saturday?
    days_since_sat = (today.weekday() - 5) % 7
    if days_since_sat == 0 and today.weekday() == 5:
        days_since_sat = 7   # today IS Saturday — use the one before
    end   = today - timedelta(days=days_since_sat)   # last Saturday
    start = end - timedelta(days=6)                  # prior Sunday
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


# ─── CANONICAL META ACTION TYPES ──────────────────────────────────────────────
#
# Meta returns the SAME event under multiple action_type names.
# Use only pixel-specific names — NEVER also add the generic short-form names
# ("purchase", "lead", "add_to_cart") because they DUPLICATE the pixel counts.
#
# Metric              Canonical key                            Do NOT also use
# ─────────────────── ──────────────────────────────────────── ───────────────
# Online purchases    offsite_conversion.fb_pixel_purchase     purchase
# Purchase value      offsite_conversion.fb_pixel_purchase     purchase (value)
# Website leads       offsite_conversion.fb_pixel_lead         lead
# Lead-gen leads      leadgen_grouped                          (no overlap)
# Add to cart         offsite_conversion.fb_pixel_add_to_cart  add_to_cart
# Checkout started    offsite_conversion.fb_pixel_initiate_checkout
# Offline purchases   offline_conversion.purchase              (no overlap)
#
# Source: Meta Ads API docs — Actions, Action Values, and Conversions


# ─── GOOGLE ADS PULL ──────────────────────────────────────────────────────────

GOOGLE_PURCHASE_CATS  = {"PURCHASE"}
GOOGLE_OFFLINE_CATS   = {"STORE_SALE"}
GOOGLE_PHONE_CATS     = {"PHONE_CALL_LEAD"}
GOOGLE_LEAD_CATS      = {
    "LEAD", "SUBMIT_LEAD_FORM", "CONTACT", "REQUEST_QUOTE",
    "BOOK_APPOINTMENT", "QUALIFIED_LEAD", "CONVERTED_LEAD",
    "IMPORT_LEAD", "SIGNUP", "REQUEST_APPOINTMENT",
}
GOOGLE_CART_CATS     = {"ADD_TO_CART"}
GOOGLE_CHECKOUT_CATS = {"BEGIN_CHECKOUT"}

_ga_service = None   # module-level cache — initialized once


def _init_google():
    """Initialize Google Ads service. Returns service or None if credentials missing."""
    global _ga_service
    if _ga_service is not None:
        return _ga_service

    missing = [k for k in (
        "GOOGLE_ADS_DEVELOPER_TOKEN", "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",   "GOOGLE_ADS_REFRESH_TOKEN",
    ) if not os.environ.get(k) or os.environ.get(k, "").startswith("your_")]

    if missing:
        print(f"\n[Google] Credentials not configured ({', '.join(missing)}).")
        print("         Add real values to .env to enable Google Ads pulls.")
        return None

    try:
        from google.ads.googleads.client import GoogleAdsClient
    except ImportError:
        print("[Google] google-ads package not installed. Run: pip3 install google-ads")
        return None

    client = GoogleAdsClient.load_from_dict({
        "developer_token":   os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
        "client_id":         os.environ["GOOGLE_ADS_CLIENT_ID"],
        "client_secret":     os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        "refresh_token":     os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
        "login_customer_id": os.environ.get("GOOGLE_ADS_CUSTOMER_ID", MCC_ID),
        "use_proto_plus":    True,
    })
    _ga_service = client.get_service("GoogleAdsService")
    return _ga_service


def _google_query(customer_id, query):
    svc = _init_google()
    if not svc:
        return []
    try:
        from google.ads.googleads.errors import GoogleAdsException
        return list(svc.search(customer_id=customer_id, query=query))
    except Exception as ex:
        msg = str(ex)
        if hasattr(ex, "failure"):
            msg = "; ".join(e.message for e in ex.failure.errors)
        print(f"  [Google API] {customer_id}: {msg}")
        return []


def pull_google(customer_id, start, end):
    """Pull Google Ads weekly data for one account. Returns metrics dict or None."""
    if not _init_google():
        return None

    base = _google_query(customer_id, f"""
        SELECT campaign.name, campaign.status, metrics.cost_micros
        FROM campaign
        WHERE segments.date BETWEEN '{start}' AND '{end}'
          AND metrics.impressions > 0
    """)
    if not base:
        return {"status": "Inactive", "spend": 0, "form_leads": 0, "call_leads": 0,
                "online_purchase": 0, "offline_purchase": 0, "purchase_value": 0,
                "add_to_carts": 0, "checkouts": 0, "notes": "No data this week"}

    total_spend = sum(r.metrics.cost_micros / 1_000_000 for r in base)
    any_enabled = any(r.campaign.status.name == "ENABLED" for r in base)

    conv_rows = _google_query(customer_id, f"""
        SELECT segments.conversion_action_category, metrics.conversions, metrics.conversions_value
        FROM campaign
        WHERE segments.date BETWEEN '{start}' AND '{end}'
    """)

    buckets = defaultdict(lambda: {"conv": 0.0, "value": 0.0})
    for r in conv_rows:
        cat = r.segments.conversion_action_category.name
        buckets[cat]["conv"]  += r.metrics.conversions
        buckets[cat]["value"] += r.metrics.conversions_value

    def s(cats, field="conv"):
        return sum(buckets[c][field] for c in cats if c in buckets)

    return {
        "status":            "Active" if any_enabled else "Inactive",
        "spend":             total_spend,
        "form_leads":        s(GOOGLE_LEAD_CATS),
        "call_leads":        s(GOOGLE_PHONE_CATS),
        "online_purchase":   s(GOOGLE_PURCHASE_CATS),
        "offline_purchase":  s(GOOGLE_OFFLINE_CATS),
        "purchase_value":    s(GOOGLE_PURCHASE_CATS, "value") + s(GOOGLE_OFFLINE_CATS, "value"),
        "add_to_carts":      s(GOOGLE_CART_CATS),
        "checkouts":         s(GOOGLE_CHECKOUT_CATS),
        "notes":             "",
    }


# ─── META ADS PULL ────────────────────────────────────────────────────────────

_meta_initialized = False


def _init_meta():
    global _meta_initialized
    if _meta_initialized:
        return True
    try:
        from facebook_business.api import FacebookAdsApi
    except ImportError:
        print("[Meta] facebook-business not installed. Run: pip3 install facebook-business")
        return False

    app_id = os.environ.get("HOSKI_META_APP_ID") or os.environ.get("META_APP_ID")
    secret = os.environ.get("HOSKI_META_APP_SECRET") or os.environ.get("META_APP_SECRET")
    token  = os.environ.get("HOSKI_META_ACCESS_TOKEN") or os.environ.get("META_ACCESS_TOKEN")

    if not all([app_id, secret, token]):
        print("[Meta] Missing META credentials in .env")
        return False

    FacebookAdsApi.init(app_id=app_id, app_secret=secret, access_token=token)
    _meta_initialized = True
    return True


def pull_meta(account_id, start, end, include_creative=True):
    """Pull Meta Ads weekly data for one account. Returns metrics dict or None."""
    if not _init_meta():
        return None

    account_id = normalize_meta_id(account_id)

    try:
        from facebook_business.adobjects.adaccount import AdAccount
        from facebook_business.exceptions import FacebookRequestError
    except ImportError:
        return None

    account = AdAccount(account_id)

    try:
        insights = list(account.get_insights(
            fields=["campaign_id", "campaign_name", "spend", "actions", "action_values"],
            params={"level": "campaign", "time_range": {"since": start, "until": end}, "limit": 500}
        ))
    except Exception as e:
        msg = e.api_error_message() if hasattr(e, "api_error_message") else str(e)
        print(f"  [Meta API] {account_id}: {msg}")
        return None

    try:
        campaigns_raw = list(account.get_campaigns(fields=["id", "status"], params={"limit": 500}))
        any_active = any(c.get("status") == "ACTIVE" for c in campaigns_raw)
    except Exception:
        any_active = False

    spend = form_leads = call_leads = 0.0
    online_purchase = offline_purchase = purchase_value = 0.0
    add_to_carts = checkouts = 0.0

    for row in insights:
        acts = {a["action_type"]: float(a["value"]) for a in (row.get("actions") or [])}
        vals = {a["action_type"]: float(a["value"]) for a in (row.get("action_values") or [])}

        spend            += float(row.get("spend", 0))
        form_leads       += (acts.get("offsite_conversion.fb_pixel_lead", 0) +
                             acts.get("leadgen_grouped", 0))
        call_leads       += acts.get("onsite_conversion.flow_complete", 0)
        online_purchase  += acts.get("offsite_conversion.fb_pixel_purchase", 0)
        offline_purchase += acts.get("offline_conversion.purchase", 0)
        purchase_value   += (vals.get("offsite_conversion.fb_pixel_purchase", 0) +
                             vals.get("offline_conversion.purchase", 0))
        add_to_carts     += acts.get("offsite_conversion.fb_pixel_add_to_cart", 0)
        checkouts        += acts.get("offsite_conversion.fb_pixel_initiate_checkout", 0)

    # Top performing creative (ad level: rank by purchases, then leads, then spend)
    top_creative_link = ""
    if include_creative:
        try:
            ad_insights = list(account.get_insights(
                fields=["ad_id", "ad_name", "spend", "actions", "action_values"],
                params={"level": "ad", "time_range": {"since": start, "until": end}, "limit": 500}
            ))

            def ad_score(r):
                a = {x["action_type"]: float(x["value"]) for x in (r.get("actions") or [])}
                return (
                    a.get("offsite_conversion.fb_pixel_purchase", 0),
                    a.get("offsite_conversion.fb_pixel_lead", 0) + a.get("leadgen_grouped", 0),
                    float(r.get("spend", 0)),
                )

            if ad_insights:
                top = max(ad_insights, key=ad_score)
                top_id = top.get("ad_id", "")
                if top_id:
                    try:
                        from facebook_business.adobjects.ad import Ad
                        from facebook_business.adobjects.adcreative import AdCreative
                        ad_obj  = Ad(top_id).api_get(fields=["creative"])
                        cr_id   = ad_obj.get("creative", {}).get("id", "")
                        if cr_id:
                            cr = AdCreative(cr_id).api_get(
                                fields=["object_story_id", "effective_object_story_id"]
                            )
                            story_id = (cr.get("effective_object_story_id") or
                                        cr.get("object_story_id", ""))
                            if story_id and "_" in story_id:
                                page_id, post_id = story_id.split("_", 1)
                                top_creative_link = (
                                    f"https://www.facebook.com/{page_id}/posts/{post_id}"
                                )
                    except Exception:
                        pass
                if not top_creative_link and top_id:
                    top_creative_link = (
                        f"https://www.facebook.com/ads/library/?id={top_id}"
                    )
        except Exception:
            pass

    return {
        "status":            "Active" if any_active else "Inactive",
        "spend":             spend,
        "form_leads":        form_leads,
        "call_leads":        call_leads,
        "online_purchase":   online_purchase,
        "offline_purchase":  offline_purchase,
        "purchase_value":    purchase_value,
        "add_to_carts":      add_to_carts,
        "checkouts":         checkouts,
        "top_creative":      top_creative_link,
        "notes":             "",
    }


# ─── CLIENT META: business context, KPI targets, known issues ────────────────
#
# vertical:       "ecom" | "lead_gen"
# roas_target:    float — ecom accounts only
# cpl_target:     float — lead gen accounts only (USD)
# monthly_calls:  int   — call-volume target (Texas FHC)
# known_issues:   dict  — platform-specific standing flags; keys: "google", "meta", "all"
#                         These appear in notes automatically until resolved.

CLIENT_META = {
    "GDM": {
        "vertical":     "ecom",
        "roas_target":  3.5,
        "known_issues": {
            "all":    "Campaigns paused Mar 18-26 (client traveling). CallRail not live — call attribution gap.",
            "google": "Offline purchase upload via Zapier may lag 24-48h; true ROAS likely higher.",
        },
    },
    "Estate Jewelry Priced Right": {
        "vertical":     "ecom",
        "roas_target":  None,
        "known_issues": {
            "google": "CRITICAL: Primary GA4 purchase conversion is HIDDEN — campaigns not optimizing toward purchases. ROAS unreliable.",
        },
    },
    "Park Road Custom Furniture and Decor": {
        "vertical":     "ecom",
        "roas_target":  5.0,
        "known_issues": {
            "all":  "Conversion tracking broken — calendar booking redirect loses Google Tag. Leads likely undercounted.",
            "meta": "Meta Ads paused since early March due to payment failure.",
        },
    },
    "FaBesthetics": {
        "vertical":    "lead_gen",
        "cpl_target":  68.57,
        "known_issues": {
            "google": "Enhanced Conversions NOT active — lead form conversions may be undercounted. Budget capped at $40/day.",
        },
    },
    "New Norseman": {
        "vertical":    "lead_gen",
        "cpl_target":  88.0,
        "known_issues": {
            "google": "Conversion tracking overlap — PMax CPL suspiciously low. New WordPress site (Mar 23) needs GTM/GA4 re-verification.",
            "meta":   "Budget capped at $30/day pending approval to scale.",
        },
    },
    "Texas FHC": {
        "vertical":       "lead_gen",
        "monthly_calls":  170,
        "known_issues": {
            "google": "New Hoski campaigns (Mar 17) in learning phase. 'Best Converters' campaign overspending vs daily budget set.",
            "meta":   "",
        },
    },
    "Dentiste": {
        "vertical":    "lead_gen",
        "cpl_target":  None,
        "known_issues": {"all": ""},
    },
    "Voit Dental 1": {
        "vertical":    "lead_gen",
        "cpl_target":  None,
        "known_issues": {
            "google": "CRITICAL: Google Ads conversion tracking broken — GHL form not firing. 0 Google conversions are likely tracking failure, not campaign failure.",
            "meta":   "Show rate 20% is #1 bottleneck. Pipeline: many leads book but don't show.",
        },
    },
    "Anand Desai Law Firm": {
        "vertical":    "lead_gen",
        "cpl_target":  None,
        "known_issues": {"all": ""},
    },
    "Serenity Familycare": {
        "vertical":    "lead_gen",
        "cpl_target":  None,
        "known_issues": {"all": ""},
    },
    "Synergy Spine & Nerve Center": {
        "vertical":    "lead_gen",
        "cpl_target":  None,
        "known_issues": {"all": ""},
    },
    "Bloomer Health": {
        "vertical":    "lead_gen",
        "cpl_target":  None,
        "known_issues": {"all": ""},
    },
    "Som K. Plastic Surgery": {
        "vertical":    "lead_gen",
        "cpl_target":  None,
        "known_issues": {"all": ""},
    },
    "Sunstone Health": {
        "vertical":    "lead_gen",
        "cpl_target":  None,
        "known_issues": {"all": ""},
    },
}


def generate_notes(client_name, platform, data):
    """
    Auto-generate 1-3 insight bullets for a client/platform row based on
    performance data vs KPI targets and known standing issues.
    Returns a semicolon-separated string.
    """
    notes = []

    spend          = data.get("spend", 0) or 0
    form_leads     = data.get("form_leads", 0) or 0
    call_leads     = data.get("call_leads", 0) or 0
    blended_leads  = form_leads + call_leads
    total_purchase = (data.get("online_purchase", 0) or 0) + (data.get("offline_purchase", 0) or 0)
    purchase_value = data.get("purchase_value", 0) or 0
    add_to_carts   = data.get("add_to_carts", 0) or 0
    checkouts      = data.get("checkouts", 0) or 0
    status         = data.get("status", "")

    meta      = CLIENT_META.get(client_name, {})
    vertical  = meta.get("vertical", "lead_gen")
    issues    = meta.get("known_issues", {})
    standing  = " ".join([issues.get("all", ""), issues.get(platform.lower(), "")]).strip()

    # ── No spend ──────────────────────────────────────────────────────────────
    if spend == 0:
        notes.append("No spend this week — account inactive")
        if standing:
            notes.append(standing)
        return "; ".join(notes)

    # ── Ecom account insights ─────────────────────────────────────────────────
    if vertical == "ecom":
        roas_target = meta.get("roas_target")
        if purchase_value > 0:
            roas = purchase_value / spend
            if roas_target:
                if roas >= roas_target:
                    notes.append(f"ROAS {roas:.2f}x — above {roas_target}x target")
                else:
                    notes.append(f"ROAS {roas:.2f}x — below {roas_target}x target")
            else:
                notes.append(f"ROAS {roas:.2f}x")
        elif total_purchase == 0 and add_to_carts == 0:
            notes.append(f"${spend:,.2f} spend, 0 purchases and 0 ATCs — check pixel/tracking")
        elif total_purchase == 0:
            notes.append(f"${spend:,.2f} spend, 0 purchases ({int(add_to_carts)} ATCs, {int(checkouts)} checkouts) — checkout drop-off")

        # Checkout friction signal
        if add_to_carts > 0 and checkouts > 0:
            checkout_rate = checkouts / add_to_carts
            if checkout_rate < 0.25:
                notes.append(f"Checkout rate {checkout_rate:.0%} — friction between cart and checkout")

    # ── Lead gen account insights ─────────────────────────────────────────────
    else:
        cpl_target    = meta.get("cpl_target")
        monthly_calls = meta.get("monthly_calls")

        if blended_leads > 0:
            cpl = spend / blended_leads
            if cpl_target:
                if cpl <= cpl_target:
                    notes.append(f"CPL ${cpl:.2f} — within ${cpl_target:.2f} target ({int(blended_leads)} leads)")
                elif cpl <= cpl_target * 1.5:
                    notes.append(f"CPL ${cpl:.2f} — {((cpl/cpl_target)-1)*100:.0f}% above ${cpl_target:.2f} target ({int(blended_leads)} leads)")
                else:
                    notes.append(f"CPL ${cpl:.2f} — FLAG: {((cpl/cpl_target)-1)*100:.0f}% above ${cpl_target:.2f} target ({int(blended_leads)} leads)")
            else:
                notes.append(f"CPL ${cpl:.2f} ({int(blended_leads)} leads: {int(form_leads)} form + {int(call_leads)} call)")

            # Calls share of blended leads
            if monthly_calls and call_leads > 0:
                notes.append(f"{int(call_leads)} call leads this week")
        else:
            notes.append(f"${spend:,.2f} spend, 0 leads — verify conversion tracking")

    # ── Standing known issues ─────────────────────────────────────────────────
    if standing:
        notes.append(standing)

    return "; ".join(n for n in notes if n)


# ─── ROW BUILDER ──────────────────────────────────────────────────────────────

REPORT_HEADERS = [
    "Week Start", "Week End",
    "Client Account", "Platform", "Account ID", "Status",
    "Amount Spend",
    "Form Leads", "Call Leads", "Blended Leads", "Blended CPL",
    "Closed Leads",
    "Online Purchase", "Offline Purchase", "Total Purchase", "Purchase Value",
    "Add to Carts", "Checkouts",
    "Total Revenue", "ROAS",
    "Top Performing Facebook Creative",
    "Notes",
    "Pulled At",
]


def _r(val, decimals=2):
    """Round numeric value or return empty string."""
    if val is None or val == 0:
        return ""
    return round(float(val), decimals)


def build_row(client_name, platform, account_id, data, week_start, week_end):
    spend           = data.get("spend", 0) or 0
    form_leads      = data.get("form_leads", 0) or 0
    call_leads      = data.get("call_leads", 0) or 0
    blended_leads   = form_leads + call_leads
    blended_cpl     = round(spend / blended_leads, 2) if blended_leads > 0 else ""
    online_purch    = data.get("online_purchase", 0) or 0
    offline_purch   = data.get("offline_purchase", 0) or 0
    total_purch     = online_purch + offline_purch
    purchase_value  = data.get("purchase_value", 0) or 0
    add_to_carts    = data.get("add_to_carts", 0) or 0
    checkouts       = data.get("checkouts", 0) or 0
    total_revenue   = purchase_value
    roas            = round(total_revenue / spend, 2) if spend > 0 and total_revenue > 0 else ""

    return [
        week_start,
        week_end,
        client_name,
        platform,
        account_id,
        data.get("status", ""),
        _r(spend),
        _r(form_leads, 0),
        _r(call_leads, 0),
        _r(blended_leads, 0),
        blended_cpl,
        "",                              # Closed Leads — manual / CRM
        _r(online_purch, 0),
        _r(offline_purch, 0),
        _r(total_purch, 0),
        _r(purchase_value),
        _r(add_to_carts, 0),
        _r(checkouts, 0),
        _r(total_revenue),
        roas,
        data.get("top_creative", ""),
        generate_notes(client_name, platform, data),
        date.today().isoformat(),
    ]


# ─── GOOGLE SHEETS WRITER ─────────────────────────────────────────────────────

TAB_NAME = "Weekly Report"


def write_to_sheet(rows, week_start, replace=False, platform_filter=None):
    """
    Write rows to the 'Weekly Report' tab, then re-sort the full sheet by
    Client (col C) then Platform (col D) so Google and Meta always appear
    together per client.

    replace=True removes existing rows that match BOTH week_start AND
    platform_filter before appending, leaving the other platform's rows
    untouched.
    """
    sheet_id   = os.environ.get("GOOGLE_SHEETS_ID")
    creds_path = os.environ.get("GOOGLE_SHEETS_CREDS_PATH",
                                str(Path(__file__).parent.parent / "sheets-credentials.json"))

    if not sheet_id:
        print("[Sheets] GOOGLE_SHEETS_ID not set in .env — skipping sheet write.")
        return
    if not Path(creds_path).exists():
        print(f"[Sheets] Service account credentials not found at: {creds_path}")
        print("         Place sheets-credentials.json in the project root.")
        return

    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        print("[Sheets] gspread not installed. Run: pip3 install gspread google-auth")
        return

    creds       = Credentials.from_service_account_file(creds_path, scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
    ])
    gc          = gspread.authorize(creds)
    spreadsheet = gc.open_by_key(sheet_id)

    try:
        ws = spreadsheet.worksheet(TAB_NAME)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=TAB_NAME, rows=5000, cols=len(REPORT_HEADERS))
        ws.append_row(REPORT_HEADERS, value_input_option="USER_ENTERED")
        print(f"[Sheets] Created tab '{TAB_NAME}' with headers.")

    if replace:
        # Remove rows matching week_start AND platform_filter (col D, index 3).
        # Rows from other platforms or other weeks are kept untouched.
        existing = ws.get_all_values()
        if len(existing) > 1:
            kept = [existing[0]]  # always keep header
            removed = 0
            for r in existing[1:]:
                week_match     = r and r[0] == week_start
                platform_match = (not platform_filter) or (len(r) > 3 and r[3] == platform_filter)
                if week_match and platform_match:
                    removed += 1
                else:
                    kept.append(r)
            ws.clear()
            if kept:
                ws.update(kept, value_input_option="USER_ENTERED")
            print(f"[Sheets] Replaced {removed} existing {platform_filter or 'all'} rows for week {week_start}.")

    ws.append_rows(rows, value_input_option="USER_ENTERED")
    print(f"[Sheets] Appended {len(rows)} rows to '{TAB_NAME}' (week {week_start}).")

    # Re-sort entire sheet by Client (col C = index 2) then Platform (col D = index 3),
    # keeping the header row pinned at the top.
    all_data = ws.get_all_values()
    if len(all_data) > 2:
        header   = all_data[0]
        data_rows = all_data[1:]
        data_rows.sort(key=lambda r: (r[2] if len(r) > 2 else "", r[3] if len(r) > 3 else ""))
        ws.clear()
        ws.update([header] + data_rows, value_input_option="USER_ENTERED")
        print(f"[Sheets] Re-sorted {len(data_rows)} rows by client and platform.")


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

DASHBOARD_TAB = "Dashboard"


def create_dashboard():
    """
    Create or refresh the Dashboard tab with QUERY() formulas that always
    show the latest week from the 'Weekly Report' tab.
    Self-updating: as new weeks are appended, the dashboard reflects the newest one.

    Layout:
      Row 1-2  : Title + week date range (MAX formula)
      Row 4    : "CLIENT DETAIL" header
      Row 5+   : QUERY table (auto-expands, one row per client x platform)
      Row 35   : "PLATFORM TOTALS" header
      Row 36+  : Aggregated QUERY by platform (spend, leads, purchases, revenue)
    """
    sheet_id   = os.environ.get("GOOGLE_SHEETS_ID")
    creds_path = os.environ.get("GOOGLE_SHEETS_CREDS_PATH",
                                str(Path(__file__).parent.parent / "sheets-credentials.json"))

    if not sheet_id or not Path(creds_path).exists():
        return  # silently skip — write_to_sheet already warned about missing config

    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        return

    creds       = Credentials.from_service_account_file(creds_path, scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
    ])
    gc          = gspread.authorize(creds)
    spreadsheet = gc.open_by_key(sheet_id)

    try:
        ws = spreadsheet.worksheet(DASHBOARD_TAB)
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=DASHBOARD_TAB, rows=200, cols=20)

    # B2 holds the latest week-start as text (yyyy-mm-dd).
    # Every QUERY references B2 so the whole dashboard self-updates each week.
    f_week_start = (
        "=TEXT(MAX(FILTER('Weekly Report'!A2:A,'Weekly Report'!A2:A<>\"\")),"
        "\"yyyy-mm-dd\")"
    )
    f_week_end = (
        "=IFERROR(TEXT(MAX(FILTER('Weekly Report'!B2:B,"
        "'Weekly Report'!A2:A=B2)),\"yyyy-mm-dd\"),\"\")"
    )

    # Detail QUERY: one row per client x platform for the latest week.
    # Weekly Report column reference:
    #   C=Client  D=Platform  F=Status  G=Spend
    #   H=Form Leads  I=Call Leads  J=Blended Leads  K=CPL
    #   O=Total Purchase  P=Purchase Value  T=ROAS  V=Notes
    # Note: column A in Weekly Report is stored as a DATE value (Sheets auto-converts
    # ISO strings on write). QUERY requires "date '...'" literal syntax for date comparisons.
    f_detail = (
        "=QUERY('Weekly Report'!A:W,"
        "\"SELECT C,D,F,G,H,I,J,K,O,P,T,V"
        " WHERE A=date '\"&B2&\"'"
        " ORDER BY C,D\",1)"
    )

    # Platform totals: one row per platform (Google / Meta) with summed KPIs.
    # Placed at a fixed row below the detail section (max ~21 client rows + buffer).
    f_totals = (
        "=QUERY('Weekly Report'!A:W,"
        "\"SELECT D,SUM(G),SUM(H),SUM(I),SUM(J),SUM(O),SUM(P)"
        " WHERE A=date '\"&B2&\"'"
        " GROUP BY D"
        " LABEL D 'Platform',SUM(G) 'Total Spend',SUM(H) 'Form Leads',"
        "SUM(I) 'Call Leads',SUM(J) 'Blended Leads',"
        "SUM(O) 'Total Purchases',SUM(P) 'Purchase Value'\",0)"
    )

    # Write header area (rows 1-4)
    ws.update(
        values=[
            ["GDM Weekly Performance Dashboard", "", "", ""],
            ["Showing week:", f_week_start, "to", f_week_end],
            ["", "", "", ""],
            ["CLIENT DETAIL - LATEST WEEK", "", "", ""],
        ],
        range_name="A1:D4",
        value_input_option="USER_ENTERED",
    )

    # Detail table at row 5 — auto-expands downward as clients are added
    ws.update(values=[[f_detail]], range_name="A5", value_input_option="USER_ENTERED")

    # Platform totals at row 35 (buffer: 21 max clients + 1 QUERY header + 8 rows spare)
    ws.update(values=[["PLATFORM TOTALS - LATEST WEEK"]], range_name="A35", value_input_option="USER_ENTERED")
    ws.update(values=[[f_totals]], range_name="A36", value_input_option="USER_ENTERED")

    # ── Currency formatting ────────────────────────────────────────────────────
    # QUERY detail (A5 = header, A6:L30 = data rows, up to 25 clients):
    #   Col D = Amount Spend, Col H = Blended CPL, Col J = Purchase Value
    # Platform totals (A36 = header, A37:G40 = data):
    #   Col B = Total Spend, Col G = Purchase Value
    currency = {"numberFormat": {"type": "CURRENCY", "pattern": "$#,##0.00"}}
    for rng in ("D6:D30", "H6:H30", "J6:J30", "B37:B40", "G37:G40"):
        ws.format(rng, currency)

    print(f"[Sheets] Dashboard '{DASHBOARD_TAB}' created/refreshed.")


# ─── TERMINAL PRINT ───────────────────────────────────────────────────────────

def print_summary(all_rows):
    print(f"\n{'='*68}")
    print(f"  {'CLIENT':<32} {'PLATFORM':<8}  {'SPEND':>8}  {'LEADS':>6}  {'PURCH':>5}  {'ROAS':>6}")
    print(f"{'─'*68}")
    for r in all_rows:
        client   = str(r[2])[:31]
        platform = str(r[3])
        spend    = f"${r[6]}" if r[6] else "—"
        leads    = str(r[9]) if r[9] != "" else "—"     # blended leads col index 9
        purch    = str(r[14]) if r[14] != "" else "—"   # total purchase
        roas     = f"{r[19]}x" if r[19] != "" else "—"  # ROAS
        print(f"  {client:<32} {platform:<8}  {spend:>8}  {leads:>6}  {purch:>5}  {roas:>6}")
    print(f"{'='*68}\n")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Weekly performance report — all clients, Google Ads + Meta Ads"
    )
    parser.add_argument("--start",        help="Week start date YYYY-MM-DD (overrides auto Sun)")
    parser.add_argument("--end",          help="Week end date YYYY-MM-DD (overrides auto Sat)")
    parser.add_argument("--client",       help="Run for a single client name (must match registry)")
    parser.add_argument("--google-only",  action="store_true", help="Skip Meta pulls")
    parser.add_argument("--meta-only",    action="store_true", help="Skip Google pulls")
    parser.add_argument("--no-creatives", action="store_true",
                        help="Skip top-creative lookup (faster, no creative link in output)")
    parser.add_argument("--no-sheet",     action="store_true", help="Skip Google Sheets write")
    parser.add_argument("--replace",       action="store_true",
                        help="Replace this week's existing rows in the sheet before appending")
    parser.add_argument("--no-dashboard",  action="store_true",
                        help="Skip Dashboard tab refresh after writing")
    args = parser.parse_args()

    week_start, week_end = last_sun_sat_week(args.start, args.end)

    print(f"\n{'='*68}")
    print(f"  WEEKLY PERFORMANCE REPORT")
    print(f"  Week: {week_start} to {week_end} (Sun-Sat)")
    print(f"{'='*68}")

    # Filter client lists if --client is passed
    google_targets = GOOGLE_CLIENTS
    meta_targets   = META_CLIENTS
    if args.client:
        google_targets = {k: v for k, v in GOOGLE_CLIENTS.items() if k == args.client}
        meta_targets   = {k: v for k, v in META_CLIENTS.items()   if k == args.client}
        if not google_targets and not meta_targets:
            print(f"  Client '{args.client}' not found in registry.")
            sys.exit(1)

    all_rows = []

    # ── Google Ads ──────────────────────────────────────────────────────────
    if not args.meta_only:
        svc_ready = _init_google() is not None
        for client_name, customer_id in google_targets.items():
            if not svc_ready:
                break
            print(f"  [Google] {client_name} ({customer_id})...", end=" ", flush=True)
            data = pull_google(customer_id, week_start, week_end)
            if data:
                row = build_row(client_name, "Google", customer_id, data, week_start, week_end)
                all_rows.append(row)
                spend = f"${data['spend']:,.2f}" if data["spend"] else "—"
                print(f"Spend: {spend}  |  Leads: {int(data['form_leads']+data['call_leads'])}  |  Status: {data['status']}")
            else:
                print("skipped")

    # ── Meta Ads ─────────────────────────────────────────────────────────────
    if not args.google_only:
        if not _init_meta():
            print("  [Meta] Could not initialize — skipping all Meta pulls.")
        else:
            for client_name, account_id in meta_targets.items():
                norm_id = normalize_meta_id(account_id)
                print(f"  [Meta]   {client_name} ({norm_id})...", end=" ", flush=True)
                data = pull_meta(norm_id, week_start, week_end,
                                 include_creative=not args.no_creatives)
                if data:
                    row = build_row(client_name, "Meta", norm_id, data, week_start, week_end)
                    all_rows.append(row)
                    spend = f"${data['spend']:,.2f}" if data["spend"] else "—"
                    roas  = f"{data['purchase_value']/data['spend']:.2f}x" if data["spend"] and data["purchase_value"] else "—"
                    print(f"Spend: {spend}  |  Purch: {int(data['online_purchase'])}  |  ROAS: {roas}  |  Status: {data['status']}")
                else:
                    print("skipped")

    if not all_rows:
        print("\n  No data pulled — nothing to write.")
        return

    print_summary(all_rows)

    # ── Google Sheets ─────────────────────────────────────────────────────────
    if not args.no_sheet:
        # Determine which platform(s) are in this run so --replace only
        # removes rows for the platforms being refreshed, not the other one.
        if args.google_only:
            platform_filter = "Google"
        elif args.meta_only:
            platform_filter = "Meta"
        else:
            platform_filter = None   # both platforms — replace all rows for the week
        write_to_sheet(all_rows, week_start, replace=args.replace,
                       platform_filter=platform_filter)
        if not args.no_dashboard:
            create_dashboard()
    else:
        print("  [Sheets] --no-sheet flag set — skipping write.")


if __name__ == "__main__":
    main()
