"""
Höski Live Dashboard Builder
Purpose: Pulls performance from Google Ads + Meta Ads for all clients,
         saves a snapshot to data/history.json, and writes docs/index.html.

Usage:
    python3 scripts/build_dashboard.py                          # last 7 days
    python3 scripts/build_dashboard.py --start 2026-04-01 --end 2026-04-30
    python3 scripts/build_dashboard.py --no-save                # skip history write

Publish:
    git add docs/index.html data/history.json
    git commit -m "chore: refresh dashboard"
    git push dashboard main
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))

_raw_password = os.environ.get("DASHBOARD_PASSWORD", "hoski2026")
PASSWORD_HASH  = hashlib.sha256(_raw_password.encode()).hexdigest()

from weekly_performance_report import (
    GOOGLE_CLIENTS,
    META_CLIENTS,
    CLIENT_META,
    pull_google,
    pull_meta,
)

OUTPUT_PATH  = PROJECT_ROOT / "docs" / "index.html"
HISTORY_PATH = PROJECT_ROOT / "data" / "history.json"


# ─── DATE RANGE ───────────────────────────────────────────────────────────────

def default_date_range():
    end   = date.today()
    start = end - timedelta(days=6)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


# ─── HISTORY ──────────────────────────────────────────────────────────────────

def load_history():
    if HISTORY_PATH.exists():
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    return []


def save_snapshot(rows, start, end, history):
    snapshot = {
        "date_start": start,
        "date_end":   end,
        "pulled_at":  date.today().isoformat(),
        "clients":    rows,
    }
    updated = [s for s in history if not (s["date_start"] == start and s["date_end"] == end)]
    updated.append(snapshot)
    updated.sort(key=lambda s: s["date_start"])
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(updated, indent=2, default=str), encoding="utf-8")
    return updated


# ─── DATA COLLECTION ──────────────────────────────────────────────────────────

ALL_CLIENTS = sorted(set(list(GOOGLE_CLIENTS.keys()) + list(META_CLIENTS.keys())))


def collect_all(start, end):
    rows = []
    total = len(ALL_CLIENTS)
    for i, name in enumerate(ALL_CLIENTS, 1):
        print(f"  [{i}/{total}] {name}")
        g_id = GOOGLE_CLIENTS.get(name)
        m_id = META_CLIENTS.get(name)

        g = pull_google(g_id, start, end) if g_id else None
        m = pull_meta(m_id, start, end, include_creative=True) if m_id else None

        meta     = CLIENT_META.get(name, {})
        vertical = meta.get("vertical", "lead_gen")

        g_spend = (g or {}).get("spend", 0) or 0
        m_spend = (m or {}).get("spend", 0) or 0
        g_form  = (g or {}).get("form_leads", 0) or 0
        m_form  = (m or {}).get("form_leads", 0) or 0
        g_call  = (g or {}).get("call_leads", 0) or 0
        m_call  = (m or {}).get("call_leads", 0) or 0
        g_purch = (g or {}).get("online_purchase", 0) or 0
        m_purch = (m or {}).get("online_purchase", 0) or 0
        g_pval  = (g or {}).get("purchase_value", 0) or 0
        m_pval  = (m or {}).get("purchase_value", 0) or 0
        g_cart  = (g or {}).get("add_to_carts", 0) or 0
        m_cart  = (m or {}).get("add_to_carts", 0) or 0
        g_ck    = (g or {}).get("checkouts", 0) or 0
        m_ck    = (m or {}).get("checkouts", 0) or 0

        total_spend = g_spend + m_spend
        total_form  = g_form + m_form
        total_call  = g_call + m_call
        blended     = total_form + total_call
        total_purch = g_purch + m_purch
        total_pval  = g_pval + m_pval
        total_cart  = g_cart + m_cart
        total_ck    = g_ck + m_ck

        rows.append({
            "name":      name,
            "vertical":  vertical,
            "google_id": g_id,
            "meta_id":   m_id,
            "combined": {
                "spend":        total_spend,
                "form_leads":   total_form,
                "call_leads":   total_call,
                "blended":      blended,
                "blended_cpl":  (total_spend / blended) if blended > 0 else None,
                "purchases":    total_purch,
                "purchase_val": total_pval,
                "add_to_carts": total_cart,
                "checkouts":    total_ck,
                "roas":         (total_pval / total_spend) if total_spend > 0 and total_pval > 0 else None,
                "top_creative": (m or {}).get("top_creative", ""),
            },
            "google": {
                "spend": g_spend, "form_leads": g_form, "call_leads": g_call,
                "purchases": g_purch, "purchase_val": g_pval,
                "add_to_carts": g_cart, "checkouts": g_ck,
            } if g else None,
            "meta": {
                "spend": m_spend, "form_leads": m_form, "call_leads": m_call,
                "purchases": m_purch, "purchase_val": m_pval,
                "add_to_carts": m_cart, "checkouts": m_ck,
                "top_creative": (m or {}).get("top_creative", ""),
            } if m else None,
        })
    return rows


# ─── FORMATTERS ───────────────────────────────────────────────────────────────

def _fmt_currency(v):
    if v is None or v == 0:
        return "$0"
    return f"${v:,.0f}" if v >= 1000 else f"${v:,.2f}"


def _fmt_num(v, decimals=0):
    if v is None:
        return "—"
    if v == 0:
        return "0"
    return f"{v:,.{decimals}f}"


def _fmt_roas(v):
    if v is None or v == 0:
        return "—"
    return f"{v:.2f}x"


# ─── HTML GENERATION ──────────────────────────────────────────────────────────

def _build_cards(rows):
    cards_html = ""
    for r in rows:
        c       = r["combined"]
        name    = r["name"]
        vert    = r["vertical"]
        is_ecom = vert == "ecom"

        tc_link = c.get("top_creative", "")
        creative_html = (
            f'<a href="{tc_link}" target="_blank" rel="noopener" class="creative-link">View Top Ad ↗</a>'
            if tc_link else '<span class="na">—</span>'
        )

        platforms = []
        if r["google_id"]:
            platforms.append('<span class="badge google">Google</span>')
        if r["meta_id"]:
            platforms.append('<span class="badge meta">Meta</span>')
        platform_badges = " ".join(platforms)

        breakdown = ""
        if r["google"] and r["meta"]:
            def brow(label, cls, d):
                rv = (d["purchase_val"] / d["spend"]) if d["spend"] > 0 and d["purchase_val"] > 0 else None
                bl = d["form_leads"] + d["call_leads"]
                cpl_v = _fmt_currency(d["spend"] / bl) if bl > 0 else "—"
                return f"""
                <tr class="breakdown-row {cls}">
                  <td><span class="badge {cls}">{label}</span></td>
                  <td>{_fmt_currency(d['spend'])}</td>
                  <td>{_fmt_num(d['form_leads'])}</td>
                  <td>{_fmt_num(d['call_leads'])}</td>
                  <td>{_fmt_num(bl)}</td>
                  <td>{cpl_v}</td>
                  <td>{"—" if not is_ecom else _fmt_num(d['purchases'])}</td>
                  <td>{"—" if not is_ecom else _fmt_currency(d['purchase_val'])}</td>
                  <td>{"—" if not is_ecom else _fmt_num(d['add_to_carts'])}</td>
                  <td>{"—" if not is_ecom else _fmt_num(d['checkouts'])}</td>
                  <td>{"—" if not is_ecom else _fmt_roas(rv)}</td>
                </tr>"""

            breakdown = f"""
            <table class="breakdown-table">
              <thead><tr>
                <th>Platform</th><th>Spend</th><th>Form</th><th>Call</th>
                <th>Leads</th><th>CPL</th><th>Purch.</th><th>Rev.</th>
                <th>ATC</th><th>CKO</th><th>ROAS</th>
              </tr></thead>
              <tbody>
                {brow('Google','google',r['google'])}
                {brow('Meta','meta',r['meta'])}
              </tbody>
            </table>"""

        blended     = c["blended"]
        cpl_display = _fmt_currency(c["blended_cpl"]) if c["blended_cpl"] else "—"
        roas_cell   = _fmt_roas(c["roas"])
        dim         = '' if is_ecom else 'style="opacity:.4"'

        cards_html += f"""
        <div class="client-card" data-vertical="{vert}" data-name="{name.lower()}">
          <div class="card-header" onclick="toggleCard(this)">
            <div class="card-title">
              <span class="client-name">{name}</span>
              {platform_badges}
            </div>
            <div class="card-summary" id="summary-{name.lower().replace(' ','-').replace('&','').replace('.','').replace('/','')}">
              <span class="metric-chip"><span class="chip-label">Spend</span><strong>{_fmt_currency(c['spend'])}</strong><span class="delta" data-metric="spend" data-client="{name}"></span></span>
              <span class="metric-chip"><span class="chip-label">Leads</span><strong>{_fmt_num(blended)}</strong><span class="delta" data-metric="blended" data-client="{name}"></span></span>
              <span class="metric-chip"><span class="chip-label">CPL</span><strong>{cpl_display}</strong><span class="delta" data-metric="blended_cpl" data-client="{name}" data-invert="1"></span></span>
              {"" if not is_ecom else f'<span class="metric-chip"><span class="chip-label">ROAS</span><strong>{roas_cell}</strong><span class="delta" data-metric="roas" data-client="{name}"></span></span>'}
            </div>
            <span class="chevron">▼</span>
          </div>
          <div class="card-body">
            <div class="sparkline-wrap">
              <canvas class="sparkline" data-client="{name}" height="60"></canvas>
            </div>
            <div class="metrics-grid">
              <div class="metric-block">
                <div class="mb-label">Spend</div>
                <div class="mb-value">{_fmt_currency(c['spend'])}</div>
              </div>
              <div class="metric-block">
                <div class="mb-label">Form Leads</div>
                <div class="mb-value">{_fmt_num(c['form_leads'])}</div>
              </div>
              <div class="metric-block">
                <div class="mb-label">Call Leads</div>
                <div class="mb-value">{_fmt_num(c['call_leads'])}</div>
              </div>
              <div class="metric-block highlight">
                <div class="mb-label">Blended Leads</div>
                <div class="mb-value">{_fmt_num(blended)}</div>
              </div>
              <div class="metric-block highlight">
                <div class="mb-label">Blended CPL</div>
                <div class="mb-value">{cpl_display}</div>
              </div>
              <div class="metric-block" {dim}>
                <div class="mb-label">Online Purchases</div>
                <div class="mb-value">{"—" if not is_ecom else _fmt_num(c['purchases'])}</div>
              </div>
              <div class="metric-block" {dim}>
                <div class="mb-label">Purchase Value</div>
                <div class="mb-value">{"—" if not is_ecom else _fmt_currency(c['purchase_val'])}</div>
              </div>
              <div class="metric-block" {dim}>
                <div class="mb-label">Add to Carts</div>
                <div class="mb-value">{"—" if not is_ecom else _fmt_num(c['add_to_carts'])}</div>
              </div>
              <div class="metric-block" {dim}>
                <div class="mb-label">Checkouts</div>
                <div class="mb-value">{"—" if not is_ecom else _fmt_num(c['checkouts'])}</div>
              </div>
              <div class="metric-block" {dim}>
                <div class="mb-label">ROAS</div>
                <div class="mb-value">{"—" if not is_ecom else roas_cell}</div>
              </div>
              <div class="metric-block creative-block">
                <div class="mb-label">Top Facebook Creative</div>
                <div class="mb-value">{creative_html}</div>
              </div>
            </div>
            {breakdown}
          </div>
        </div>"""
    return cards_html


def render_html(rows, start, end, history=None):
    if history is None:
        history = []

    pulled_at   = date.today().strftime("%B %d, %Y")
    total_spend = sum(r["combined"]["spend"] for r in rows)
    total_leads = sum(r["combined"]["blended"] for r in rows)
    avg_cpl     = (total_spend / total_leads) if total_leads > 0 else 0
    total_rev   = sum(r["combined"]["purchase_val"] for r in rows)

    cards_html    = _build_cards(rows)
    history_json  = json.dumps(history, default=str)

    # Snapshot picker options (newest first)
    picker_opts = ""
    for i, snap in enumerate(reversed(history)):
        label   = f"{snap['date_start']} → {snap['date_end']}"
        current = snap["date_start"] == start and snap["date_end"] == end
        sel     = " selected" if current else ""
        rev_idx = len(history) - 1 - i
        picker_opts += f'<option value="{rev_idx}"{sel}>{label}</option>\n'
    if not picker_opts:
        picker_opts = f'<option value="-1">{start} → {end}</option>\n'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Höski — Paid Ads Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js"></script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          background: #0f172a; color: #e2e8f0; min-height: 100vh; }}
  a {{ color: inherit; }}
  .container {{ max-width: 1400px; margin: 0 auto; padding: 1.5rem; }}

  /* ── Header ── */
  header {{ padding: 1.5rem 0 1rem; border-bottom: 1px solid #1e293b; margin-bottom: 1.5rem;
            display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:.5rem; }}
  header h1 {{ font-size: 1.4rem; font-weight: 700; letter-spacing: -0.02em; color: #f8fafc; }}
  .header-meta {{ font-size: .8rem; color: #64748b; }}
  .snapshot-picker {{ background: #1e293b; border: 1px solid #334155; color: #e2e8f0;
                       border-radius: 6px; padding: .3rem .7rem; font-size: .8rem; outline: none; cursor: pointer; }}
  .snapshot-picker:focus {{ border-color: #475569; }}

  /* ── Scorecards ── */
  .scorecards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }}
  .sc {{ background: #1e293b; border-radius: 10px; padding: 1rem 1.25rem; }}
  .sc .sc-label {{ font-size: .7rem; text-transform: uppercase; letter-spacing: .08em; color: #64748b; margin-bottom: .3rem; }}
  .sc .sc-value {{ font-size: 1.5rem; font-weight: 700; color: #f8fafc; }}

  /* ── Trend charts ── */
  .trends-section {{ margin-bottom: 2rem; }}
  .trends-title {{ font-size: .75rem; text-transform: uppercase; letter-spacing: .08em;
                    color: #64748b; margin-bottom: .75rem; }}
  .trends-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }}
  .trend-box {{ background: #1e293b; border-radius: 10px; padding: 1rem 1.25rem; }}
  .trend-box .t-label {{ font-size: .7rem; text-transform: uppercase; letter-spacing: .07em;
                          color: #64748b; margin-bottom: .6rem; }}
  .trend-box canvas {{ max-height: 120px; }}

  /* ── Filters ── */
  .filters {{ display: flex; gap: .5rem; margin-bottom: 1.25rem; flex-wrap: wrap; align-items: center; }}
  .filters label {{ font-size: .75rem; color: #64748b; margin-right: .25rem; }}
  .filter-btn {{ background: #1e293b; border: 1px solid #334155; color: #94a3b8; border-radius: 6px;
                  padding: .35rem .9rem; font-size: .8rem; cursor: pointer; transition: all .15s; }}
  .filter-btn:hover, .filter-btn.active {{ background: #334155; color: #f8fafc; border-color: #475569; }}
  .search-input {{ background: #1e293b; border: 1px solid #334155; color: #e2e8f0; border-radius: 6px;
                    padding: .35rem .8rem; font-size: .8rem; width: 200px; outline: none; }}
  .search-input:focus {{ border-color: #475569; }}
  .search-input::placeholder {{ color: #475569; }}
  .expand-ctrl {{ font-size: .75rem; color: #64748b; cursor: pointer; margin-left: auto;
                   text-decoration: underline; text-underline-offset: 2px; }}
  .expand-ctrl:hover {{ color: #94a3b8; }}

  /* ── Client cards ── */
  .clients-list {{ display: flex; flex-direction: column; gap: .75rem; }}
  .client-card {{ background: #1e293b; border-radius: 10px; overflow: hidden; border: 1px solid #263148; }}
  .card-header {{ display: flex; align-items: center; gap: 1rem; padding: .9rem 1.25rem; cursor: pointer;
                   user-select: none; transition: background .15s; flex-wrap: wrap; }}
  .card-header:hover {{ background: #243048; }}
  .card-title {{ display: flex; align-items: center; gap: .6rem; flex: 1; min-width: 200px; }}
  .client-name {{ font-weight: 600; font-size: .95rem; color: #f1f5f9; }}
  .card-summary {{ display: flex; gap: .75rem; flex-wrap: wrap; }}
  .metric-chip {{ display: flex; align-items: center; gap: .3rem; font-size: .8rem; }}
  .chip-label {{ color: #64748b; font-size: .7rem; }}
  .metric-chip strong {{ color: #e2e8f0; }}
  .chevron {{ color: #475569; font-size: .75rem; transition: transform .2s; margin-left: auto; }}
  .card-header.open .chevron {{ transform: rotate(180deg); }}

  /* WoW delta badges */
  .delta {{ font-size: .68rem; font-weight: 600; padding: .1rem .3rem; border-radius: 3px; }}
  .delta.up   {{ color: #4ade80; background: #052e16; }}
  .delta.down {{ color: #f87171; background: #2d0a0a; }}

  /* Card body */
  .card-body {{ display: none; padding: 1rem 1.25rem 1.25rem; border-top: 1px solid #263148; }}
  .card-body.open {{ display: block; }}
  .sparkline-wrap {{ margin-bottom: .75rem; }}
  .sparkline {{ width: 100% !important; }}

  /* Metrics grid */
  .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: .75rem; margin-bottom: 1rem; }}
  .metric-block {{ background: #0f172a; border-radius: 8px; padding: .75rem 1rem; }}
  .metric-block.highlight {{ border: 1px solid #334155; }}
  .metric-block.creative-block {{ grid-column: span 2; }}
  .mb-label {{ font-size: .65rem; text-transform: uppercase; letter-spacing: .07em; color: #64748b; margin-bottom: .25rem; }}
  .mb-value {{ font-size: 1.1rem; font-weight: 600; color: #f1f5f9; }}
  .creative-link {{ color: #60a5fa; text-decoration: none; font-size: .9rem; }}
  .creative-link:hover {{ text-decoration: underline; }}
  .na {{ color: #475569; }}

  /* Platform badges */
  .badge {{ display: inline-block; font-size: .65rem; font-weight: 600; border-radius: 4px;
             padding: .15rem .45rem; text-transform: uppercase; letter-spacing: .04em; }}
  .badge.google {{ background: #1a3a6b; color: #93c5fd; }}
  .badge.meta   {{ background: #1a2f5e; color: #a5b4fc; }}

  /* Breakdown table */
  .breakdown-table {{ width: 100%; border-collapse: collapse; font-size: .78rem; margin-top: .25rem; overflow-x: auto; display: block; }}
  .breakdown-table th {{ color: #64748b; font-weight: 500; text-align: left; padding: .4rem .6rem; border-bottom: 1px solid #1e293b; white-space: nowrap; }}
  .breakdown-table td {{ padding: .4rem .6rem; border-bottom: 1px solid #131e2e; color: #cbd5e1; white-space: nowrap; }}

  /* Password gate */
  .gate {{ position: fixed; inset: 0; background: #0f172a; display: flex;
           align-items: center; justify-content: center; z-index: 9999; }}
  .gate-box {{ background: #1e293b; border: 1px solid #334155; border-radius: 14px;
               padding: 2.5rem 2rem; width: 100%; max-width: 340px; text-align: center; }}
  .gate-box h2 {{ font-size: 1.2rem; font-weight: 700; color: #f8fafc; margin-bottom: .4rem; }}
  .gate-box p  {{ font-size: .8rem; color: #64748b; margin-bottom: 1.25rem; }}
  .gate-input {{ width: 100%; background: #0f172a; border: 1px solid #334155; color: #e2e8f0;
                  border-radius: 8px; padding: .6rem .9rem; font-size: .9rem; outline: none; margin-bottom: .75rem; }}
  .gate-input:focus {{ border-color: #475569; }}
  .gate-btn {{ width: 100%; background: #3b82f6; color: #fff; border: none; border-radius: 8px;
               padding: .65rem; font-size: .9rem; font-weight: 600; cursor: pointer; transition: background .15s; }}
  .gate-btn:hover {{ background: #2563eb; }}
  .gate-error {{ font-size: .78rem; color: #f87171; margin-top: .6rem; display: none; }}

  @media (max-width: 700px) {{
    .metrics-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .metric-block.creative-block {{ grid-column: span 2; }}
  }}
</style>
</head>
<body>

<div class="gate" id="gate">
  <div class="gate-box">
    <h2>Höski Dashboard</h2>
    <p>Enter password to access</p>
    <input class="gate-input" type="password" id="pwdInput" placeholder="Password" />
    <button class="gate-btn" onclick="checkPassword()">Enter</button>
    <div class="gate-error" id="pwdError">Incorrect password</div>
  </div>
</div>

<div id="app" style="display:none">
<div class="container">

  <header>
    <div>
      <h1>Höski — Paid Ads Dashboard</h1>
      <div class="header-meta">Updated {pulled_at}</div>
    </div>
    <div style="display:flex;align-items:center;gap:.75rem;">
      <span class="header-meta">Period:</span>
      <select class="snapshot-picker" id="snapshotPicker" onchange="selectSnapshot(parseInt(this.value))">
        {picker_opts}
      </select>
    </div>
  </header>

  <div class="scorecards" id="scorecards">
    <div class="sc"><div class="sc-label">Total Spend</div><div class="sc-value" id="sc-spend">{_fmt_currency(total_spend)}</div></div>
    <div class="sc"><div class="sc-label">Total Leads</div><div class="sc-value" id="sc-leads">{_fmt_num(total_leads)}</div></div>
    <div class="sc"><div class="sc-label">Avg CPL</div><div class="sc-value" id="sc-cpl">{"—" if total_leads == 0 else _fmt_currency(avg_cpl)}</div></div>
    <div class="sc"><div class="sc-label">Total Revenue (ecom)</div><div class="sc-value" id="sc-rev">{_fmt_currency(total_rev)}</div></div>
    <div class="sc"><div class="sc-label">Clients Tracked</div><div class="sc-value">{len(rows)}</div></div>
  </div>

  <div class="trends-section" id="trendsSection" style="{'display:none' if len(history) < 2 else ''}">
    <div class="trends-title">Historical Trends</div>
    <div class="trends-grid">
      <div class="trend-box"><div class="t-label">Total Spend</div><canvas id="trendSpend"></canvas></div>
      <div class="trend-box"><div class="t-label">Total Leads</div><canvas id="trendLeads"></canvas></div>
      <div class="trend-box"><div class="t-label">Avg CPL</div><canvas id="trendCPL"></canvas></div>
      <div class="trend-box"><div class="t-label">Ecom Revenue</div><canvas id="trendRev"></canvas></div>
    </div>
  </div>

  <div class="filters">
    <label>Filter:</label>
    <button class="filter-btn active" onclick="filterCards('all', this)">All clients</button>
    <button class="filter-btn" onclick="filterCards('ecom', this)">Ecom / DTC</button>
    <button class="filter-btn" onclick="filterCards('lead_gen', this)">Lead Gen</button>
    <button class="filter-btn" onclick="filterCards('google-only', this)">Google only</button>
    <button class="filter-btn" onclick="filterCards('meta-only', this)">Meta only</button>
    <input class="search-input" type="search" placeholder="Search client..." oninput="searchClients(this.value)" />
    <span class="expand-ctrl" onclick="expandAll()">Expand all</span>
  </div>

  <div class="clients-list" id="clientsList">
    {cards_html}
  </div>

</div>
</div>

<script>
const PW_HASH = "{PASSWORD_HASH}";
const HISTORY = {history_json};

// ── Auth ──────────────────────────────────────────────────────────────────────
async function sha256(str) {{
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str));
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2,'0')).join('');
}}
async function checkPassword() {{
  const hash = await sha256(document.getElementById('pwdInput').value);
  if (hash === PW_HASH) {{
    sessionStorage.setItem('hoski_auth', PW_HASH);
    document.getElementById('gate').style.display = 'none';
    document.getElementById('app').style.display  = '';
    initCharts();
  }} else {{
    document.getElementById('pwdError').style.display = 'block';
    document.getElementById('pwdInput').focus();
  }}
}}
document.getElementById('pwdInput').addEventListener('keydown', e => {{ if (e.key==='Enter') checkPassword(); }});
(async () => {{
  if (sessionStorage.getItem('hoski_auth') === PW_HASH) {{
    document.getElementById('gate').style.display = 'none';
    document.getElementById('app').style.display  = '';
    initCharts();
  }}
}})();

// ── Formatters ────────────────────────────────────────────────────────────────
function fmtCurrency(v) {{
  if (!v) return '$0';
  return v >= 1000 ? '$' + v.toLocaleString('en-US', {{maximumFractionDigits:0}}) : '$' + v.toFixed(2);
}}
function fmtNum(v) {{
  if (v === null || v === undefined) return '—';
  return v === 0 ? '0' : v.toLocaleString('en-US', {{maximumFractionDigits:0}});
}}
function fmtRoas(v) {{ return (!v || v === 0) ? '—' : v.toFixed(2) + 'x'; }}

// ── Trend charts ──────────────────────────────────────────────────────────────
const CHART_OPTS = (yFmt) => ({{
  responsive: true, maintainAspectRatio: true,
  plugins: {{ legend: {{ display: false }}, tooltip: {{
    callbacks: {{ label: ctx => yFmt(ctx.parsed.y) }},
    backgroundColor: '#1e293b', titleColor: '#94a3b8', bodyColor: '#e2e8f0',
  }} }},
  scales: {{
    x: {{ ticks: {{ color: '#64748b', font: {{size:10}} }}, grid: {{ color: '#1e293b' }} }},
    y: {{ ticks: {{ color: '#64748b', font: {{size:10}}, callback: v => yFmt(v) }}, grid: {{ color: '#1e293b' }} }},
  }},
}});

const LINE_DS = (data, color) => ({{
  data, borderColor: color, backgroundColor: color + '22',
  fill: true, tension: 0.3, pointRadius: 4, pointHoverRadius: 6,
}});

let trendCharts = {{}};

function initCharts() {{
  if (HISTORY.length < 2) return;
  const labels  = HISTORY.map(s => s.date_end.slice(5));
  const spends  = HISTORY.map(s => s.clients.reduce((a,c) => a + (c.combined.spend||0), 0));
  const leads   = HISTORY.map(s => s.clients.reduce((a,c) => a + (c.combined.blended||0), 0));
  const cpls    = HISTORY.map((s,i) => leads[i] > 0 ? spends[i]/leads[i] : 0);
  const revs    = HISTORY.map(s => s.clients.filter(c=>c.vertical==='ecom').reduce((a,c) => a + (c.combined.purchase_val||0), 0));

  const mk = (id, data, color, fmt) => {{
    const ctx = document.getElementById(id)?.getContext('2d');
    if (!ctx) return;
    if (trendCharts[id]) trendCharts[id].destroy();
    trendCharts[id] = new Chart(ctx, {{ type:'line', data:{{ labels, datasets:[LINE_DS(data,color)] }}, options: CHART_OPTS(fmt) }});
  }};
  mk('trendSpend', spends, '#3b82f6', fmtCurrency);
  mk('trendLeads', leads,  '#10b981', fmtNum);
  mk('trendCPL',   cpls,   '#f59e0b', fmtCurrency);
  mk('trendRev',   revs,   '#8b5cf6', fmtCurrency);
  document.getElementById('trendsSection').style.display = '';
}}

// ── WoW deltas ────────────────────────────────────────────────────────────────
function applyDeltas(snapIdx) {{
  document.querySelectorAll('.delta').forEach(el => {{ el.textContent = ''; el.className = 'delta'; }});
  if (snapIdx < 1 || snapIdx >= HISTORY.length) return;
  const curr = HISTORY[snapIdx];
  const prev = HISTORY[snapIdx - 1];
  curr.clients.forEach(client => {{
    const prevClient = prev.clients.find(c => c.name === client.name);
    if (!prevClient) return;
    [
      {{ metric:'spend',       invert:false }},
      {{ metric:'blended',     invert:false }},
      {{ metric:'blended_cpl', invert:true  }},
      {{ metric:'roas',        invert:false }},
    ].forEach(({{metric, invert}}) => {{
      const cur = client.combined[metric];
      const prv = prevClient.combined[metric];
      if (!cur || !prv || prv === 0) return;
      const pct   = ((cur - prv) / prv) * 100;
      const isGood = invert ? pct < 0 : pct > 0;
      document.querySelectorAll(`.delta[data-metric="${{metric}}"][data-client="${{client.name}}"]`).forEach(el => {{
        el.textContent = (pct > 0 ? '▲' : '▼') + ' ' + Math.abs(pct).toFixed(0) + '%';
        el.className   = 'delta ' + (isGood ? 'up' : 'down');
      }});
    }});
  }});
}}

// ── Snapshot picker ───────────────────────────────────────────────────────────
let sparklineCharts = {{}};

function selectSnapshot(snapIdx) {{
  if (snapIdx < 0 || snapIdx >= HISTORY.length) return;
  const snap    = HISTORY[snapIdx];
  const clients = snap.clients;
  const list    = document.getElementById('clientsList');

  // Re-render cards
  list.innerHTML = clients.map(client => buildCard(client)).join('');

  // Update scorecards
  const totalSpend = clients.reduce((a,c) => a+(c.combined.spend||0),0);
  const totalLeads = clients.reduce((a,c) => a+(c.combined.blended||0),0);
  const avgCPL     = totalLeads > 0 ? totalSpend/totalLeads : 0;
  const totalRev   = clients.filter(c=>c.vertical==='ecom').reduce((a,c) => a+(c.combined.purchase_val||0),0);
  document.getElementById('sc-spend').textContent = fmtCurrency(totalSpend);
  document.getElementById('sc-leads').textContent = fmtNum(totalLeads);
  document.getElementById('sc-cpl').textContent   = totalLeads > 0 ? fmtCurrency(avgCPL) : '—';
  document.getElementById('sc-rev').textContent   = fmtCurrency(totalRev);

  applyDeltas(snapIdx);
  sparklineCharts = {{}};
}}

// ── JS card builder (used for historical snapshots) ───────────────────────────
function buildCard(r) {{
  const c       = r.combined;
  const isEcom  = r.vertical === 'ecom';
  const dim     = isEcom ? '' : 'style="opacity:.4"';
  const cpl     = c.blended_cpl ? fmtCurrency(c.blended_cpl) : '—';
  const roas    = fmtRoas(c.roas);
  const tc      = c.top_creative ? `<a href="${{c.top_creative}}" target="_blank" class="creative-link">View Top Ad ↗</a>` : '<span class="na">—</span>';
  const gBadge  = r.google_id ? '<span class="badge google">Google</span>' : '';
  const mBadge  = r.meta_id   ? '<span class="badge meta">Meta</span>'   : '';
  const roasChip = isEcom ? `<span class="metric-chip"><span class="chip-label">ROAS</span><strong>${{roas}}</strong><span class="delta" data-metric="roas" data-client="${{r.name}}"></span></span>` : '';

  let bdown = '';
  if (r.google && r.meta) {{
    const mkRow = (label, cls, d) => {{
      const bl  = (d.form_leads||0) + (d.call_leads||0);
      const rv  = d.spend > 0 && d.purchase_val > 0 ? d.purchase_val/d.spend : null;
      return `<tr class="breakdown-row ${{cls}}">
        <td><span class="badge ${{cls}}">${{label}}</span></td>
        <td>${{fmtCurrency(d.spend)}}</td><td>${{fmtNum(d.form_leads)}}</td><td>${{fmtNum(d.call_leads)}}</td>
        <td>${{fmtNum(bl)}}</td><td>${{bl>0?fmtCurrency(d.spend/bl):'—'}}</td>
        <td>${{isEcom?fmtNum(d.purchases):'—'}}</td><td>${{isEcom?fmtCurrency(d.purchase_val):'—'}}</td>
        <td>${{isEcom?fmtNum(d.add_to_carts):'—'}}</td><td>${{isEcom?fmtNum(d.checkouts):'—'}}</td>
        <td>${{isEcom?fmtRoas(rv):'—'}}</td>
      </tr>`;
    }};
    bdown = `<table class="breakdown-table"><thead><tr>
      <th>Platform</th><th>Spend</th><th>Form</th><th>Call</th>
      <th>Leads</th><th>CPL</th><th>Purch.</th><th>Rev.</th><th>ATC</th><th>CKO</th><th>ROAS</th>
    </tr></thead><tbody>${{mkRow('Google','google',r.google)}}${{mkRow('Meta','meta',r.meta)}}</tbody></table>`;
  }}

  return `<div class="client-card" data-vertical="${{r.vertical}}" data-name="${{r.name.toLowerCase()}}">
    <div class="card-header" onclick="toggleCard(this)">
      <div class="card-title"><span class="client-name">${{r.name}}</span>${{gBadge}}${{mBadge}}</div>
      <div class="card-summary">
        <span class="metric-chip"><span class="chip-label">Spend</span><strong>${{fmtCurrency(c.spend)}}</strong><span class="delta" data-metric="spend" data-client="${{r.name}}"></span></span>
        <span class="metric-chip"><span class="chip-label">Leads</span><strong>${{fmtNum(c.blended)}}</strong><span class="delta" data-metric="blended" data-client="${{r.name}}"></span></span>
        <span class="metric-chip"><span class="chip-label">CPL</span><strong>${{cpl}}</strong><span class="delta" data-metric="blended_cpl" data-client="${{r.name}}" data-invert="1"></span></span>
        ${{roasChip}}
      </div>
      <span class="chevron">▼</span>
    </div>
    <div class="card-body">
      <div class="sparkline-wrap"><canvas class="sparkline" data-client="${{r.name}}" height="60"></canvas></div>
      <div class="metrics-grid">
        <div class="metric-block"><div class="mb-label">Spend</div><div class="mb-value">${{fmtCurrency(c.spend)}}</div></div>
        <div class="metric-block"><div class="mb-label">Form Leads</div><div class="mb-value">${{fmtNum(c.form_leads)}}</div></div>
        <div class="metric-block"><div class="mb-label">Call Leads</div><div class="mb-value">${{fmtNum(c.call_leads)}}</div></div>
        <div class="metric-block highlight"><div class="mb-label">Blended Leads</div><div class="mb-value">${{fmtNum(c.blended)}}</div></div>
        <div class="metric-block highlight"><div class="mb-label">Blended CPL</div><div class="mb-value">${{cpl}}</div></div>
        <div class="metric-block" ${{dim}}><div class="mb-label">Online Purchases</div><div class="mb-value">${{isEcom?fmtNum(c.purchases):'—'}}</div></div>
        <div class="metric-block" ${{dim}}><div class="mb-label">Purchase Value</div><div class="mb-value">${{isEcom?fmtCurrency(c.purchase_val):'—'}}</div></div>
        <div class="metric-block" ${{dim}}><div class="mb-label">Add to Carts</div><div class="mb-value">${{isEcom?fmtNum(c.add_to_carts):'—'}}</div></div>
        <div class="metric-block" ${{dim}}><div class="mb-label">Checkouts</div><div class="mb-value">${{isEcom?fmtNum(c.checkouts):'—'}}</div></div>
        <div class="metric-block" ${{dim}}><div class="mb-label">ROAS</div><div class="mb-value">${{isEcom?roas:'—'}}</div></div>
        <div class="metric-block creative-block"><div class="mb-label">Top Facebook Creative</div><div class="mb-value">${{tc}}</div></div>
      </div>
      ${{bdown}}
    </div>
  </div>`;
}}

// ── Sparklines (lazy, per card) ───────────────────────────────────────────────
function initSparkline(canvas) {{
  const clientName = canvas.dataset.client;
  if (sparklineCharts[clientName]) return;
  if (HISTORY.length < 2) {{ canvas.style.display='none'; return; }}
  const labels = HISTORY.map(s => s.date_end.slice(5));
  const data   = HISTORY.map(s => {{
    const c = s.clients.find(cl => cl.name === clientName);
    return c ? (c.combined.spend || 0) : 0;
  }});
  const ctx = canvas.getContext('2d');
  sparklineCharts[clientName] = new Chart(ctx, {{
    type: 'line',
    data: {{ labels, datasets: [{{ data, borderColor:'#3b82f6', backgroundColor:'#3b82f611',
                                   fill:true, tension:0.3, pointRadius:3 }}] }},
    options: {{
      responsive:true, maintainAspectRatio:false,
      plugins: {{ legend:{{display:false}}, tooltip:{{ callbacks:{{ label: ctx => fmtCurrency(ctx.parsed.y) }} }} }},
      scales: {{
        x: {{ ticks:{{ color:'#64748b', font:{{size:9}} }}, grid:{{color:'#1e293b'}} }},
        y: {{ ticks:{{ color:'#64748b', font:{{size:9}}, callback: v => fmtCurrency(v) }}, grid:{{color:'#1e293b'}} }},
      }},
    }},
  }});
}}

// ── Card interactions ─────────────────────────────────────────────────────────
function toggleCard(header) {{
  header.classList.toggle('open');
  const body = header.nextElementSibling;
  body.classList.toggle('open');
  if (body.classList.contains('open')) {{
    const canvas = body.querySelector('.sparkline');
    if (canvas) initSparkline(canvas);
  }}
}}

function expandAll() {{
  const headers = document.querySelectorAll('.card-header');
  const anyOpen = [...headers].some(h => h.classList.contains('open'));
  headers.forEach(h => {{
    const body = h.nextElementSibling;
    if (anyOpen) {{ h.classList.remove('open'); body.classList.remove('open'); }}
    else {{
      h.classList.add('open'); body.classList.add('open');
      const canvas = body.querySelector('.sparkline');
      if (canvas) initSparkline(canvas);
    }}
  }});
  document.querySelector('.expand-ctrl').textContent = anyOpen ? 'Expand all' : 'Collapse all';
}}

function filterCards(type, btn) {{
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.client-card').forEach(card => {{
    const vert = card.dataset.vertical;
    const hasG = card.querySelector('.badge.google');
    const hasM = card.querySelector('.badge.meta');
    let show = true;
    if      (type==='ecom')        show = vert==='ecom';
    else if (type==='lead_gen')    show = vert==='lead_gen';
    else if (type==='google-only') show = hasG && !hasM;
    else if (type==='meta-only')   show = hasM && !hasG;
    card.style.display = show ? '' : 'none';
  }});
}}

function searchClients(q) {{
  const term = q.toLowerCase();
  document.querySelectorAll('.client-card').forEach(card => {{
    card.style.display = card.dataset.name.includes(term) ? '' : 'none';
  }});
  if (q === '') document.querySelectorAll('.filter-btn.active')[0]?.click();
}}

// ── Init WoW deltas for the default (latest) snapshot ────────────────────────
(function() {{
  const picker = document.getElementById('snapshotPicker');
  if (picker && HISTORY.length >= 2) {{
    applyDeltas(parseInt(picker.value));
  }}
}})();
</script>
</body>
</html>"""


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Build Höski paid ads dashboard")
    parser.add_argument("--start",   help="Start date YYYY-MM-DD (default: 7 days ago)")
    parser.add_argument("--end",     help="End date YYYY-MM-DD (default: today)")
    parser.add_argument("--no-save", action="store_true", help="Skip saving snapshot to history.json")
    args = parser.parse_args()

    if args.start and args.end:
        start, end = args.start, args.end
    else:
        start, end = default_date_range()

    print(f"\nHöski Dashboard Builder")
    print(f"Date range : {start} → {end}")
    print(f"Pulling data for {len(ALL_CLIENTS)} clients...\n")

    rows    = collect_all(start, end)
    history = load_history()

    if not args.no_save:
        history = save_snapshot(rows, start, end, history)
        print(f"Snapshot saved. History: {len(history)} period(s) on record.")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    html = render_html(rows, start, end, history)
    OUTPUT_PATH.write_text(html, encoding="utf-8")

    print(f"\nDone. Dashboard written to: {OUTPUT_PATH}")
    print(f"\nTo publish:")
    print(f"  git add docs/index.html data/history.json")
    print(f'  git commit -m "chore: refresh dashboard {end}"')
    print(f"  git push dashboard main")


if __name__ == "__main__":
    main()
