"""
HTML Weekly Performance Report Generator
Purpose: Reads the "Weekly Report" Google Sheet tab and generates docs/index.html
         — a self-contained interactive report hosted via GitHub Pages.

Usage:
    python3 scripts/generate_html_report.py

    Then commit and push docs/index.html to GitHub for GitHub Pages to serve it.

Environment:
    GOOGLE_SHEETS_ID          Sheet ID (from .env)
    GOOGLE_SHEETS_CREDS_PATH  Path to service account JSON (default: sheets-credentials.json)
"""

import json
import os
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_CREDS_PATH = PROJECT_ROOT / "sheets-credentials.json"
OUTPUT_PATH = PROJECT_ROOT / "docs" / "index.html"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

# Clients that are ecom / have ROAS data worth showing
ECOM_CLIENTS = {
    "GDM",
    "New Norseman",
    "Estate Jewelry Priced Right",
    "Park Road Custom Furniture and Decor",
}

PLATFORM_COLORS = {
    "Google": "#4285F4",
    "Meta":   "#1877F2",
}


# ─── AUTH ─────────────────────────────────────────────────────────────────────

def get_sheet_records():
    creds_path = os.environ.get("GOOGLE_SHEETS_CREDS_PATH", str(DEFAULT_CREDS_PATH))
    sheet_id   = os.environ.get("GOOGLE_SHEETS_ID")
    if not sheet_id:
        print("[Error] GOOGLE_SHEETS_ID not set in .env")
        sys.exit(1)
    if not Path(creds_path).exists():
        print(f"[Error] Credentials not found at: {creds_path}")
        sys.exit(1)
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    gc    = gspread.authorize(creds)
    ws    = gc.open_by_key(sheet_id).worksheet("Weekly Report")
    return ws.get_all_records()


# ─── DATA HELPERS ─────────────────────────────────────────────────────────────

def _f(val):
    """Parse a value that may be a float, '$1,234.56' string, or empty."""
    if val is None or val == "":
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    return float(str(val).replace("$", "").replace(",", "").strip() or 0)


def process_records(records):
    """
    Returns:
        weeks          — sorted list of week-start strings (newest first)
        by_week        — {week_start: [row, ...]}
        by_client      — {client: {platform: row}}  (latest week only)
        weekly_totals  — {week_start: {spend, leads, revenue, roas_num, roas_den}}
        platform_trend — {platform: {week_start: {spend, leads}}}
    """
    # Column names from get_all_records() come from row 1 headers
    # Sheet columns A-W:
    #   Week Start, Week End, Client Account, Platform, Account ID, Status,
    #   Amount Spend, Form Leads, Call Leads, Blended Leads, Blended CPL,
    #   Appointment Booked, Online Purchase, Offline Purchase / Closed Leads,
    #   Total Purchase, Purchase Value, Add to Carts, Checkouts,
    #   Total Revenue, ROAS, Top Performing Facebook Creative, Notes, Pulled At

    by_week    = defaultdict(list)
    by_client  = defaultdict(dict)
    weekly_totals   = defaultdict(lambda: {"spend": 0, "leads": 0, "revenue": 0, "roas_num": 0, "roas_den": 0})
    platform_trend  = defaultdict(lambda: defaultdict(lambda: {"spend": 0, "leads": 0}))

    for r in records:
        week  = str(r.get("Week Start", "")).strip()
        if not week:
            continue
        client   = str(r.get("Client Account", "")).strip()
        platform = str(r.get("Platform", "")).strip()
        spend    = _f(r.get("Amount Spend", 0))
        leads    = _f(r.get("Blended Leads", 0))
        revenue  = _f(r.get("Total Revenue", 0))
        roas     = _f(r.get("ROAS", 0))

        by_week[week].append(r)
        by_client[client][platform] = r

        weekly_totals[week]["spend"]    += spend
        weekly_totals[week]["leads"]    += leads
        weekly_totals[week]["revenue"]  += revenue
        if roas:
            weekly_totals[week]["roas_num"] += spend * roas
            weekly_totals[week]["roas_den"] += spend

        platform_trend[platform][week]["spend"] += spend
        platform_trend[platform][week]["leads"] += leads

    weeks = sorted(by_week.keys(), reverse=True)
    return weeks, dict(by_week), dict(by_client), dict(weekly_totals), dict(platform_trend)


def build_chart_data(weeks, weekly_totals, platform_trend):
    """Build Chart.js-ready JSON payloads."""
    sorted_weeks = sorted(weeks)  # oldest → newest for trend charts

    # Weekly trend: spend and leads by platform
    google_spend = [platform_trend.get("Google", {}).get(w, {}).get("spend", 0) for w in sorted_weeks]
    meta_spend   = [platform_trend.get("Meta",   {}).get(w, {}).get("spend", 0) for w in sorted_weeks]
    google_leads = [platform_trend.get("Google", {}).get(w, {}).get("leads", 0) for w in sorted_weeks]
    meta_leads   = [platform_trend.get("Meta",   {}).get(w, {}).get("leads", 0) for w in sorted_weeks]

    trend = {
        "labels": sorted_weeks,
        "google_spend": google_spend,
        "meta_spend":   meta_spend,
        "google_leads": google_leads,
        "meta_leads":   meta_leads,
    }

    return trend


def build_client_bar_data(latest_week_rows):
    """Aggregate spend and leads by client for the latest week."""
    client_data = defaultdict(lambda: {"spend": 0, "leads": 0})
    for r in latest_week_rows:
        c = str(r.get("Client Account", "")).strip()
        client_data[c]["spend"] += _f(r.get("Amount Spend", 0))
        client_data[c]["leads"] += _f(r.get("Blended Leads", 0))

    # Sort by spend descending
    sorted_clients = sorted(client_data.items(), key=lambda x: x[1]["spend"], reverse=True)
    return {
        "clients": [c for c, _ in sorted_clients],
        "spend":   [round(v["spend"], 2) for _, v in sorted_clients],
        "leads":   [round(v["leads"], 1) for _, v in sorted_clients],
    }


# ─── HTML TEMPLATE ────────────────────────────────────────────────────────────

def build_table_rows(rows):
    html = ""
    for r in sorted(rows, key=lambda x: _f(x.get("Amount Spend", 0)), reverse=True):
        client   = r.get("Client Account", "")
        platform = r.get("Platform", "")
        status   = r.get("Status", "")
        spend    = _f(r.get("Amount Spend", 0))
        f_leads  = _f(r.get("Form Leads", 0))
        c_leads  = _f(r.get("Call Leads", 0))
        b_leads  = _f(r.get("Blended Leads", 0))
        cpl      = _f(r.get("Blended CPL", 0))
        appt     = _f(r.get("Appointment Booked", 0))
        purch    = _f(r.get("Total Purchase", 0))
        revenue  = _f(r.get("Total Revenue", 0))
        roas     = _f(r.get("ROAS", 0))
        notes    = str(r.get("Notes", "")).strip()

        plat_color = PLATFORM_COLORS.get(platform, "#888")
        badge = f'<span class="badge" style="background:{plat_color}">{platform}</span>'
        roas_cell = f"{roas:.2f}x" if roas else "—"
        cpl_cell  = f"${cpl:,.2f}" if cpl else "—"
        appt_cell = str(int(appt)) if appt else "—"
        purch_cell = str(int(purch)) if purch else "—"
        rev_cell  = f"${revenue:,.2f}" if revenue else "—"

        html += f"""
        <tr>
          <td>{client}</td>
          <td>{badge}</td>
          <td>${spend:,.2f}</td>
          <td>{int(f_leads)}</td>
          <td>{int(c_leads)}</td>
          <td>{int(b_leads)}</td>
          <td>{cpl_cell}</td>
          <td>{appt_cell}</td>
          <td>{purch_cell}</td>
          <td>{rev_cell}</td>
          <td>{roas_cell}</td>
          <td class="notes-cell">{notes}</td>
        </tr>"""
    return html


def build_roas_table(latest_week_rows):
    html = ""
    ecom_rows = [r for r in latest_week_rows if str(r.get("Client Account", "")).strip() in ECOM_CLIENTS]
    if not ecom_rows:
        return "<p>No e-commerce data for this week.</p>"
    for r in sorted(ecom_rows, key=lambda x: _f(x.get("ROAS", 0)), reverse=True):
        client  = r.get("Client Account", "")
        platform = r.get("Platform", "")
        spend   = _f(r.get("Amount Spend", 0))
        revenue = _f(r.get("Total Revenue", 0))
        roas    = _f(r.get("ROAS", 0))
        plat_color = PLATFORM_COLORS.get(platform, "#888")
        badge = f'<span class="badge" style="background:{plat_color}">{platform}</span>'
        roas_color = "#22c55e" if roas >= 3 else ("#f59e0b" if roas >= 1.5 else "#ef4444")
        html += f"""
        <tr>
          <td>{client}</td>
          <td>{badge}</td>
          <td>${spend:,.2f}</td>
          <td>${revenue:,.2f}</td>
          <td style="color:{roas_color};font-weight:600">{roas:.2f}x</td>
        </tr>"""
    return html


def generate_html(
    weeks, by_week, weekly_totals, trend_data, client_bar, generated_at
):
    latest_week = weeks[0] if weeks else ""
    prev_week   = weeks[1] if len(weeks) > 1 else None
    latest_rows = by_week.get(latest_week, [])

    totals = weekly_totals.get(latest_week, {})
    spend   = totals.get("spend", 0)
    leads   = totals.get("leads", 0)
    revenue = totals.get("revenue", 0)
    roas_n  = totals.get("roas_num", 0)
    roas_d  = totals.get("roas_den", 0)
    avg_cpl = (spend / leads) if leads else 0
    blended_roas = (roas_n / roas_d) if roas_d else 0

    # WoW deltas
    def wow_delta(metric, cur_week, prv_week):
        if not prv_week:
            return ""
        cur = weekly_totals.get(cur_week, {}).get(metric, 0)
        prv = weekly_totals.get(prv_week, {}).get(metric, 0)
        if not prv:
            return ""
        pct = ((cur - prv) / prv) * 100
        arrow = "▲" if pct >= 0 else "▼"
        color = "#22c55e" if pct >= 0 else "#ef4444"
        return f'<span style="color:{color};font-size:0.8em"> {arrow} {abs(pct):.1f}% WoW</span>'

    table_rows = build_table_rows(latest_rows)
    roas_rows  = build_roas_table(latest_rows)

    trend_json    = json.dumps(trend_data)
    client_json   = json.dumps(client_bar)

    week_end = by_week.get(latest_week, [{}])[0].get("Week End", "") if latest_rows else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Höski Marketing — Weekly Performance Report</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js"></script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          background: #0f172a; color: #e2e8f0; min-height: 100vh; }}
  .container {{ max-width: 1400px; margin: 0 auto; padding: 1.5rem; }}

  /* ── Header ── */
  header {{ padding: 2rem 0 1rem; border-bottom: 1px solid #1e293b; margin-bottom: 2rem; }}
  header h1 {{ font-size: 1.6rem; font-weight: 700; letter-spacing: -0.02em; color: #f8fafc; }}
  header p  {{ color: #64748b; font-size: 0.875rem; margin-top: 0.25rem; }}

  /* ── Scorecards ── */
  .scorecards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .card {{ background: #1e293b; border-radius: 12px; padding: 1.25rem 1.5rem; }}
  .card .label {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b; margin-bottom: 0.4rem; }}
  .card .value {{ font-size: 1.75rem; font-weight: 700; color: #f8fafc; }}
  .card .delta {{ font-size: 0.8rem; margin-top: 0.25rem; }}

  /* ── Section headers ── */
  .section-title {{ font-size: 1rem; font-weight: 600; color: #94a3b8;
                    text-transform: uppercase; letter-spacing: 0.06em;
                    margin-bottom: 1rem; }}

  /* ── Charts grid ── */
  .charts-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2rem; }}
  @media (max-width: 900px) {{ .charts-grid {{ grid-template-columns: 1fr; }} }}
  .chart-box {{ background: #1e293b; border-radius: 12px; padding: 1.25rem; }}
  .chart-box canvas {{ max-height: 280px; }}

  /* ── Trend chart full-width ── */
  .trend-box {{ background: #1e293b; border-radius: 12px; padding: 1.25rem; margin-bottom: 2rem; }}
  .trend-box canvas {{ max-height: 240px; }}

  /* ── Tables ── */
  .table-wrap {{ overflow-x: auto; background: #1e293b; border-radius: 12px; margin-bottom: 2rem; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
  thead th {{ background: #0f172a; color: #64748b; font-weight: 600;
              text-transform: uppercase; letter-spacing: 0.05em;
              padding: 0.75rem 1rem; text-align: left; white-space: nowrap;
              cursor: pointer; user-select: none; }}
  thead th:hover {{ color: #94a3b8; }}
  tbody tr {{ border-top: 1px solid #0f172a; }}
  tbody tr:hover {{ background: #263352; }}
  tbody td {{ padding: 0.65rem 1rem; white-space: nowrap; }}
  .notes-cell {{ white-space: normal; max-width: 260px; font-size: 0.8rem; color: #94a3b8; }}

  .badge {{ display: inline-block; padding: 0.15em 0.55em; border-radius: 4px;
            font-size: 0.7rem; font-weight: 700; color: #fff; letter-spacing: 0.03em; }}

  /* ── ROAS table ── */
  .roas-table-wrap {{ overflow-x: auto; background: #1e293b; border-radius: 12px; margin-bottom: 2rem; }}

  /* ── Footer ── */
  footer {{ color: #334155; font-size: 0.75rem; text-align: center; padding: 2rem 0 1rem; }}
</style>
</head>
<body>
<div class="container">

  <header>
    <h1>Höski Marketing Manager</h1>
    <p>Weekly Performance Report &mdash; {latest_week} to {week_end} &nbsp;&bull;&nbsp; Generated {generated_at}</p>
  </header>

  <!-- Scorecards -->
  <div class="scorecards">
    <div class="card">
      <div class="label">Total Spend</div>
      <div class="value">${spend:,.0f}</div>
      <div class="delta">{wow_delta("spend", latest_week, prev_week)}</div>
    </div>
    <div class="card">
      <div class="label">Total Leads</div>
      <div class="value">{leads:,.0f}</div>
      <div class="delta">{wow_delta("leads", latest_week, prev_week)}</div>
    </div>
    <div class="card">
      <div class="label">Avg CPL</div>
      <div class="value">${avg_cpl:,.2f}</div>
      <div class="delta"></div>
    </div>
    <div class="card">
      <div class="label">Total Revenue</div>
      <div class="value">${revenue:,.0f}</div>
      <div class="delta">{wow_delta("revenue", latest_week, prev_week)}</div>
    </div>
    <div class="card">
      <div class="label">Blended ROAS</div>
      <div class="value">{blended_roas:.2f}x</div>
      <div class="delta"></div>
    </div>
  </div>

  <!-- Client bar charts -->
  <div class="charts-grid">
    <div class="chart-box">
      <div class="section-title">Spend by Client (this week)</div>
      <canvas id="spendChart"></canvas>
    </div>
    <div class="chart-box">
      <div class="section-title">Leads by Client (this week)</div>
      <canvas id="leadsChart"></canvas>
    </div>
  </div>

  <!-- Weekly trend -->
  <div class="trend-box">
    <div class="section-title">Weekly Trend — Spend (Google vs Meta)</div>
    <canvas id="trendSpendChart"></canvas>
  </div>
  <div class="trend-box">
    <div class="section-title">Weekly Trend — Leads (Google vs Meta)</div>
    <canvas id="trendLeadsChart"></canvas>
  </div>

  <!-- Full KPI table -->
  <div class="section-title">Client &times; Platform Detail — {latest_week} to {week_end}</div>
  <div class="table-wrap">
    <table id="kpiTable">
      <thead>
        <tr>
          <th onclick="sortTable(0)">Client</th>
          <th onclick="sortTable(1)">Platform</th>
          <th onclick="sortTable(2)">Spend</th>
          <th onclick="sortTable(3)">Form Leads</th>
          <th onclick="sortTable(4)">Call Leads</th>
          <th onclick="sortTable(5)">Blended Leads</th>
          <th onclick="sortTable(6)">Blended CPL</th>
          <th onclick="sortTable(7)">Appt Booked</th>
          <th onclick="sortTable(8)">Purchases</th>
          <th onclick="sortTable(9)">Revenue</th>
          <th onclick="sortTable(10)">ROAS</th>
          <th>Notes</th>
        </tr>
      </thead>
      <tbody>
        {table_rows}
      </tbody>
    </table>
  </div>

  <!-- ROAS / Ecom table -->
  <div class="section-title">E-commerce ROAS Summary</div>
  <div class="roas-table-wrap">
    <table>
      <thead>
        <tr>
          <th>Client</th><th>Platform</th><th>Spend</th><th>Revenue</th><th>ROAS</th>
        </tr>
      </thead>
      <tbody>
        {roas_rows}
      </tbody>
    </table>
  </div>

  <footer>Höski Marketing Manager &mdash; auto-generated &mdash; {generated_at}</footer>
</div>

<script>
const TREND   = {trend_json};
const CLIENTS = {client_json};

const chartDefaults = {{
  color: '#94a3b8',
  plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }},
  scales: {{
    x: {{ ticks: {{ color: '#64748b' }}, grid: {{ color: '#1e293b' }} }},
    y: {{ ticks: {{ color: '#64748b' }}, grid: {{ color: '#1e293b' }} }},
  }},
}};

function barChart(id, labels, datasets) {{
  new Chart(document.getElementById(id), {{
    type: 'bar',
    data: {{ labels, datasets }},
    options: {{
      indexAxis: 'y',
      responsive: true,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        x: {{ ticks: {{ color: '#64748b' }}, grid: {{ color: '#0f172a' }} }},
        y: {{ ticks: {{ color: '#94a3b8', font: {{ size: 11 }} }}, grid: {{ color: '#0f172a' }} }},
      }},
    }},
  }});
}}

function lineChart(id, labels, datasets, label_y) {{
  new Chart(document.getElementById(id), {{
    type: 'line',
    data: {{ labels, datasets }},
    options: {{
      responsive: true,
      interaction: {{ mode: 'index', intersect: false }},
      plugins: chartDefaults.plugins,
      scales: {{
        x: {{ ticks: {{ color: '#64748b' }}, grid: {{ color: '#1e293b' }} }},
        y: {{ ticks: {{ color: '#64748b' }}, grid: {{ color: '#1e293b' }}, title: {{ display: !!label_y, text: label_y, color: '#64748b' }} }},
      }},
    }},
  }});
}}

barChart('spendChart', CLIENTS.clients, [{{
  data: CLIENTS.spend,
  backgroundColor: '#4285F4',
  borderRadius: 4,
}}]);

barChart('leadsChart', CLIENTS.clients, [{{
  data: CLIENTS.leads,
  backgroundColor: '#1877F2',
  borderRadius: 4,
}}]);

lineChart('trendSpendChart', TREND.labels, [
  {{ label: 'Google Spend', data: TREND.google_spend, borderColor: '#4285F4', backgroundColor: 'rgba(66,133,244,0.1)', fill: true, tension: 0.3 }},
  {{ label: 'Meta Spend',   data: TREND.meta_spend,   borderColor: '#1877F2', backgroundColor: 'rgba(24,119,242,0.1)', fill: true, tension: 0.3 }},
], 'Spend ($)');

lineChart('trendLeadsChart', TREND.labels, [
  {{ label: 'Google Leads', data: TREND.google_leads, borderColor: '#34d399', backgroundColor: 'rgba(52,211,153,0.1)', fill: true, tension: 0.3 }},
  {{ label: 'Meta Leads',   data: TREND.meta_leads,   borderColor: '#f59e0b', backgroundColor: 'rgba(245,158,11,0.1)',  fill: true, tension: 0.3 }},
], 'Leads');

// ── Sortable table ──────────────────────────────────────────────────────────
let sortDir = {{}};
function sortTable(col) {{
  const tbl  = document.getElementById('kpiTable');
  const tbody = tbl.querySelector('tbody');
  const rows  = Array.from(tbody.querySelectorAll('tr'));
  const asc   = !sortDir[col];
  sortDir = {{ [col]: asc }};
  rows.sort((a, b) => {{
    const av = a.cells[col].innerText.trim().replace(/[$,x]/g, '');
    const bv = b.cells[col].innerText.trim().replace(/[$,x]/g, '');
    const an = parseFloat(av), bn = parseFloat(bv);
    if (!isNaN(an) && !isNaN(bn)) return asc ? an - bn : bn - an;
    return asc ? av.localeCompare(bv) : bv.localeCompare(av);
  }});
  rows.forEach(r => tbody.appendChild(r));
}}
</script>
</body>
</html>"""


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("[HTML Report] Reading sheet data...")
    records = get_sheet_records()
    print(f"[HTML Report] {len(records)} rows loaded")

    weeks, by_week, by_client, weekly_totals, platform_trend = process_records(records)

    if not weeks:
        print("[HTML Report] No data found in sheet. Exiting.")
        sys.exit(1)

    print(f"[HTML Report] Latest week: {weeks[0]} | Total weeks: {len(weeks)}")

    trend_data  = build_chart_data(weeks, weekly_totals, platform_trend)
    client_bar  = build_client_bar_data(by_week.get(weeks[0], []))
    generated_at = date.today().isoformat()

    html = generate_html(weeks, by_week, weekly_totals, trend_data, client_bar, generated_at)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"[HTML Report] Written to: {OUTPUT_PATH}")
    print(f"[HTML Report] Open in browser: file://{OUTPUT_PATH.resolve()}")
    print()
    print("Next steps to publish:")
    print("  git add docs/index.html docs/.nojekyll")
    print('  git commit -m "chore: update weekly HTML report"')
    print("  git push")
    print("  → Live at: https://bishalbarua.github.io/google-ads-manager/")


if __name__ == "__main__":
    main()
