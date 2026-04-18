"""
Höski Live Dashboard Builder
Purpose: Pulls last-7-days performance from Google Ads + Meta Ads for all
         clients and writes docs/index.html — a self-contained dashboard
         hosted via GitHub Pages.

Usage:
    python3 scripts/build_dashboard.py

Then commit and push docs/index.html:
    git add docs/index.html && git commit -m "chore: refresh dashboard" && git push
"""

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

# Password protection — set DASHBOARD_PASSWORD in .env to override.
# Default: hoski2026
_raw_password = os.environ.get("DASHBOARD_PASSWORD", "hoski2026")
PASSWORD_HASH  = hashlib.sha256(_raw_password.encode()).hexdigest()

from weekly_performance_report import (
    GOOGLE_CLIENTS,
    META_CLIENTS,
    CLIENT_META,
    normalize_meta_id,
    pull_google,
    pull_meta,
)

OUTPUT_PATH = PROJECT_ROOT / "docs" / "index.html"


# ─── DATE RANGE ───────────────────────────────────────────────────────────────

def last_7_days():
    end   = date.today()
    start = end - timedelta(days=6)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


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

        meta = CLIENT_META.get(name, {})
        vertical = meta.get("vertical", "lead_gen")

        g_spend        = (g or {}).get("spend", 0) or 0
        m_spend        = (m or {}).get("spend", 0) or 0
        g_form         = (g or {}).get("form_leads", 0) or 0
        m_form         = (m or {}).get("form_leads", 0) or 0
        g_call         = (g or {}).get("call_leads", 0) or 0
        m_call         = (m or {}).get("call_leads", 0) or 0
        g_purch        = (g or {}).get("online_purchase", 0) or 0
        m_purch        = (m or {}).get("online_purchase", 0) or 0
        g_pval         = (g or {}).get("purchase_value", 0) or 0
        m_pval         = (m or {}).get("purchase_value", 0) or 0
        g_cart         = (g or {}).get("add_to_carts", 0) or 0
        m_cart         = (m or {}).get("add_to_carts", 0) or 0
        g_ck           = (g or {}).get("checkouts", 0) or 0
        m_ck           = (m or {}).get("checkouts", 0) or 0

        total_spend    = g_spend + m_spend
        total_form     = g_form + m_form
        total_call     = g_call + m_call
        blended        = total_form + total_call
        blended_cpl    = (total_spend / blended) if blended > 0 else None
        total_purch    = g_purch + m_purch
        total_pval     = g_pval + m_pval
        total_cart     = g_cart + m_cart
        total_ck       = g_ck + m_ck
        roas           = (total_pval / total_spend) if total_spend > 0 and total_pval > 0 else None
        top_creative   = (m or {}).get("top_creative", "")

        rows.append({
            "name":         name,
            "vertical":     vertical,
            "google_id":    g_id,
            "meta_id":      m_id,
            "combined": {
                "spend":        total_spend,
                "form_leads":   total_form,
                "call_leads":   total_call,
                "blended":      blended,
                "blended_cpl":  blended_cpl,
                "purchases":    total_purch,
                "purchase_val": total_pval,
                "add_to_carts": total_cart,
                "checkouts":    total_ck,
                "roas":         roas,
                "top_creative": top_creative,
            },
            "google": {
                "spend":        g_spend,
                "form_leads":   g_form,
                "call_leads":   g_call,
                "purchases":    g_purch,
                "purchase_val": g_pval,
                "add_to_carts": g_cart,
                "checkouts":    g_ck,
            } if g else None,
            "meta": {
                "spend":        m_spend,
                "form_leads":   m_form,
                "call_leads":   m_call,
                "purchases":    m_purch,
                "purchase_val": m_pval,
                "add_to_carts": m_cart,
                "checkouts":    m_ck,
                "top_creative": top_creative,
            } if m else None,
        })
    return rows


# ─── HTML GENERATION ──────────────────────────────────────────────────────────

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


def render_html(rows, start, end):
    pulled_at  = date.today().strftime("%B %d, %Y")
    total_spend = sum(r["combined"]["spend"] for r in rows)
    total_leads = sum(r["combined"]["blended"] for r in rows)
    avg_cpl     = (total_spend / total_leads) if total_leads > 0 else 0
    total_rev   = sum(r["combined"]["purchase_val"] for r in rows)

    # Serialize rows to JSON for JS
    js_data = json.dumps(rows, default=str)

    # Build client cards HTML
    cards_html = ""
    for r in rows:
        c = r["combined"]
        name   = r["name"]
        vert   = r["vertical"]
        is_ecom = vert == "ecom"

        roas_cell    = _fmt_roas(c["roas"])
        tc_link      = c.get("top_creative", "")
        creative_html = (
            f'<a href="{tc_link}" target="_blank" rel="noopener" class="creative-link">View Top Ad ↗</a>'
            if tc_link else '<span class="na">—</span>'
        )

        # Platform badges
        platforms = []
        if r["google_id"]:
            platforms.append('<span class="badge google">Google</span>')
        if r["meta_id"]:
            platforms.append('<span class="badge meta">Meta</span>')
        platform_badges = " ".join(platforms)

        # Breakdown rows (Google / Meta)
        breakdown = ""
        if r["google"] and r["meta"]:
            def brow(label, cls, d):
                is_ecom_row = vert == "ecom"
                roas_v = (d["purchase_val"] / d["spend"]) if d["spend"] > 0 and d["purchase_val"] > 0 else None
                return f"""
                <tr class="breakdown-row {cls}">
                  <td><span class="badge {cls}">{label}</span></td>
                  <td>{_fmt_currency(d['spend'])}</td>
                  <td>{_fmt_num(d['form_leads'])}</td>
                  <td>{_fmt_num(d['call_leads'])}</td>
                  <td>{_fmt_num(d['form_leads'] + d['call_leads'])}</td>
                  <td>{"—" if (d['form_leads']+d['call_leads']) == 0 else _fmt_currency(d['spend']/(d['form_leads']+d['call_leads'])) if (d['form_leads']+d['call_leads']) > 0 else "—"}</td>
                  <td>{"—" if not is_ecom_row else _fmt_num(d['purchases'])}</td>
                  <td>{"—" if not is_ecom_row else _fmt_currency(d['purchase_val'])}</td>
                  <td>{"—" if not is_ecom_row else _fmt_num(d['add_to_carts'])}</td>
                  <td>{"—" if not is_ecom_row else _fmt_num(d['checkouts'])}</td>
                  <td>{"—" if not is_ecom_row else _fmt_roas(roas_v)}</td>
                  <td>—</td>
                </tr>"""

            breakdown = f"""
            <table class="breakdown-table">
              <thead><tr>
                <th>Platform</th><th>Spend</th><th>Form</th><th>Call</th>
                <th>Total</th><th>CPL</th><th>Purch.</th><th>Rev.</th>
                <th>ATC</th><th>CKO</th><th>ROAS</th><th>Top Creative</th>
              </tr></thead>
              <tbody>
                {brow('Google','google',r['google'])}
                {brow('Meta','meta',r['meta'])}
              </tbody>
            </table>"""

        ecom_hidden = "" if is_ecom else " style=\"display:none\""
        ecom_na     = "—" if not is_ecom else ""

        blended_leads = c["blended"]
        blended_cpl_display = _fmt_currency(c["blended_cpl"]) if c["blended_cpl"] else "—"

        cards_html += f"""
        <div class="client-card" data-vertical="{vert}" data-name="{name.lower()}">
          <div class="card-header" onclick="toggleCard(this)">
            <div class="card-title">
              <span class="client-name">{name}</span>
              {platform_badges}
            </div>
            <div class="card-summary">
              <span class="metric-chip"><span class="chip-label">Spend</span><strong>{_fmt_currency(c['spend'])}</strong></span>
              <span class="metric-chip"><span class="chip-label">Leads</span><strong>{_fmt_num(blended_leads)}</strong></span>
              <span class="metric-chip"><span class="chip-label">CPL</span><strong>{blended_cpl_display}</strong></span>
              {"" if not is_ecom else f'<span class="metric-chip"><span class="chip-label">ROAS</span><strong>{roas_cell}</strong></span>'}
            </div>
            <span class="chevron">▼</span>
          </div>
          <div class="card-body">
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
                <div class="mb-value">{_fmt_num(blended_leads)}</div>
              </div>
              <div class="metric-block highlight">
                <div class="mb-label">Blended CPL</div>
                <div class="mb-value">{blended_cpl_display}</div>
              </div>
              <div class="metric-block" {"" if is_ecom else 'style="opacity:.4"'}>
                <div class="mb-label">Online Purchases</div>
                <div class="mb-value">{"—" if not is_ecom else _fmt_num(c['purchases'])}</div>
              </div>
              <div class="metric-block" {"" if is_ecom else 'style="opacity:.4"'}>
                <div class="mb-label">Purchase Value</div>
                <div class="mb-value">{"—" if not is_ecom else _fmt_currency(c['purchase_val'])}</div>
              </div>
              <div class="metric-block" {"" if is_ecom else 'style="opacity:.4"'}>
                <div class="mb-label">Add to Carts</div>
                <div class="mb-value">{"—" if not is_ecom else _fmt_num(c['add_to_carts'])}</div>
              </div>
              <div class="metric-block" {"" if is_ecom else 'style="opacity:.4"'}>
                <div class="mb-label">Checkouts</div>
                <div class="mb-value">{"—" if not is_ecom else _fmt_num(c['checkouts'])}</div>
              </div>
              <div class="metric-block" {"" if is_ecom else 'style="opacity:.4"'}>
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

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Höski — Paid Ads Dashboard</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          background: #0f172a; color: #e2e8f0; min-height: 100vh; }}
  a {{ color: inherit; }}

  /* ── Layout ── */
  .container {{ max-width: 1400px; margin: 0 auto; padding: 1.5rem; }}

  /* ── Header ── */
  header {{ padding: 1.5rem 0 1rem; border-bottom: 1px solid #1e293b; margin-bottom: 1.5rem; display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:.5rem; }}
  header h1 {{ font-size: 1.4rem; font-weight: 700; letter-spacing: -0.02em; color: #f8fafc; }}
  .header-meta {{ font-size: .8rem; color: #64748b; }}

  /* ── Summary scorecards ── */
  .scorecards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }}
  .sc {{ background: #1e293b; border-radius: 10px; padding: 1rem 1.25rem; }}
  .sc .sc-label {{ font-size: .7rem; text-transform: uppercase; letter-spacing: .08em; color: #64748b; margin-bottom: .3rem; }}
  .sc .sc-value {{ font-size: 1.5rem; font-weight: 700; color: #f8fafc; }}

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

  /* ── Client cards ── */
  .clients-list {{ display: flex; flex-direction: column; gap: .75rem; }}
  .client-card {{ background: #1e293b; border-radius: 10px; overflow: hidden; border: 1px solid #263148; }}

  /* Card header */
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

  /* Card body */
  .card-body {{ display: none; padding: 1rem 1.25rem 1.25rem; border-top: 1px solid #263148; }}
  .card-body.open {{ display: block; }}

  /* Metrics grid */
  .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: .75rem; margin-bottom: 1rem; }}
  .metric-block {{ background: #0f172a; border-radius: 8px; padding: .75rem 1rem; }}
  .metric-block.highlight {{ border: 1px solid #334155; }}
  .metric-block.creative-block {{ grid-column: span 2; }}
  .mb-label {{ font-size: .65rem; text-transform: uppercase; letter-spacing: .07em; color: #64748b; margin-bottom: .25rem; }}
  .mb-value {{ font-size: 1.1rem; font-weight: 600; color: #f1f5f9; }}

  /* Creative link */
  .creative-link {{ color: #60a5fa; text-decoration: none; font-size: .9rem; }}
  .creative-link:hover {{ text-decoration: underline; }}
  .na {{ color: #475569; }}

  /* Platform badges */
  .badge {{ display: inline-block; font-size: .65rem; font-weight: 600; border-radius: 4px;
             padding: .15rem .45rem; text-transform: uppercase; letter-spacing: .04em; }}
  .badge.google {{ background: #1a3a6b; color: #93c5fd; }}
  .badge.meta   {{ background: #1a2f5e; color: #a5b4fc; }}

  /* Breakdown table */
  .breakdown-table {{ width: 100%; border-collapse: collapse; font-size: .78rem; margin-top: .25rem; }}
  .breakdown-table th {{ color: #64748b; font-weight: 500; text-align: left; padding: .4rem .6rem; border-bottom: 1px solid #1e293b; }}
  .breakdown-table td {{ padding: .4rem .6rem; border-bottom: 1px solid #131e2e; color: #cbd5e1; }}
  .breakdown-row.google td:first-child .badge {{ background: #1a3a6b; color: #93c5fd; }}
  .breakdown-row.meta td:first-child .badge   {{ background: #1a2f5e; color: #a5b4fc; }}

  /* Expand all toggle */
  .expand-ctrl {{ font-size: .75rem; color: #64748b; cursor: pointer; margin-left: auto; text-decoration: underline; text-underline-offset: 2px; }}
  .expand-ctrl:hover {{ color: #94a3b8; }}

  /* Responsive */
  @media (max-width: 700px) {{
    .metrics-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .metric-block.creative-block {{ grid-column: span 2; }}
    .breakdown-table {{ font-size: .7rem; }}
  }}

  /* ── Password gate ── */
  .gate {{ position: fixed; inset: 0; background: #0f172a; display: flex;
           align-items: center; justify-content: center; z-index: 9999; }}
  .gate-box {{ background: #1e293b; border: 1px solid #334155; border-radius: 14px;
               padding: 2.5rem 2rem; width: 100%; max-width: 340px; text-align: center; }}
  .gate-box h2 {{ font-size: 1.2rem; font-weight: 700; color: #f8fafc; margin-bottom: .4rem; }}
  .gate-box p  {{ font-size: .8rem; color: #64748b; margin-bottom: 1.25rem; }}
  .gate-input {{ width: 100%; background: #0f172a; border: 1px solid #334155; color: #e2e8f0;
                  border-radius: 8px; padding: .6rem .9rem; font-size: .9rem;
                  outline: none; margin-bottom: .75rem; }}
  .gate-input:focus {{ border-color: #475569; }}
  .gate-btn {{ width: 100%; background: #3b82f6; color: #fff; border: none;
               border-radius: 8px; padding: .65rem; font-size: .9rem; font-weight: 600;
               cursor: pointer; transition: background .15s; }}
  .gate-btn:hover {{ background: #2563eb; }}
  .gate-error {{ font-size: .78rem; color: #f87171; margin-top: .6rem; display: none; }}
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
      <div class="header-meta">
        {start} &nbsp;→&nbsp; {end} &nbsp;·&nbsp; Last 7 days
      </div>
    </div>
    <div class="header-meta">Updated {pulled_at}</div>
  </header>

  <div class="scorecards">
    <div class="sc"><div class="sc-label">Total Spend</div><div class="sc-value">{_fmt_currency(total_spend)}</div></div>
    <div class="sc"><div class="sc-label">Total Leads</div><div class="sc-value">{_fmt_num(total_leads)}</div></div>
    <div class="sc"><div class="sc-label">Avg CPL</div><div class="sc-value">{"—" if total_leads == 0 else _fmt_currency(avg_cpl)}</div></div>
    <div class="sc"><div class="sc-label">Total Revenue (ecom)</div><div class="sc-value">{_fmt_currency(total_rev)}</div></div>
    <div class="sc"><div class="sc-label">Clients Active</div><div class="sc-value">{len(rows)}</div></div>
  </div>

  <div class="filters">
    <label>Filter:</label>
    <button class="filter-btn active" onclick="filter('all', this)">All clients</button>
    <button class="filter-btn" onclick="filter('ecom', this)">Ecom / DTC</button>
    <button class="filter-btn" onclick="filter('lead_gen', this)">Lead Gen</button>
    <button class="filter-btn" onclick="filter('google-only', this)">Google only</button>
    <button class="filter-btn" onclick="filter('meta-only', this)">Meta only</button>
    <input class="search-input" type="search" placeholder="Search client..." oninput="searchClients(this.value)" />
    <span class="expand-ctrl" onclick="expandAll()">Expand all</span>
  </div>

  <div class="clients-list" id="clientsList">
    {cards_html}
  </div>

</div>
</div><!-- #app -->

<script>
  const PW_HASH = "{PASSWORD_HASH}";

  async function sha256(str) {{
    const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str));
    return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
  }}

  async function checkPassword() {{
    const val  = document.getElementById('pwdInput').value;
    const hash = await sha256(val);
    if (hash === PW_HASH) {{
      sessionStorage.setItem('hoski_auth', PW_HASH);
      document.getElementById('gate').style.display = 'none';
      document.getElementById('app').style.display  = '';
    }} else {{
      document.getElementById('pwdError').style.display = 'block';
      document.getElementById('pwdInput').focus();
    }}
  }}

  document.getElementById('pwdInput').addEventListener('keydown', e => {{
    if (e.key === 'Enter') checkPassword();
  }});

  // Auto-unlock if already authenticated this session
  (async () => {{
    if (sessionStorage.getItem('hoski_auth') === PW_HASH) {{
      document.getElementById('gate').style.display = 'none';
      document.getElementById('app').style.display  = '';
    }}
  }})();

  function toggleCard(header) {{
    header.classList.toggle('open');
    const body = header.nextElementSibling;
    body.classList.toggle('open');
  }}

  function expandAll() {{
    const headers = document.querySelectorAll('.card-header');
    const anyOpen = [...headers].some(h => h.classList.contains('open'));
    headers.forEach(h => {{
      const body = h.nextElementSibling;
      if (anyOpen) {{ h.classList.remove('open'); body.classList.remove('open'); }}
      else {{ h.classList.add('open'); body.classList.add('open'); }}
    }});
    const ctrl = document.querySelector('.expand-ctrl');
    ctrl.textContent = anyOpen ? 'Expand all' : 'Collapse all';
  }}

  function filter(type, btn) {{
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('.client-card').forEach(card => {{
      const vert   = card.dataset.vertical;
      const hasG   = card.querySelector('.badge.google');
      const hasM   = card.querySelector('.badge.meta');
      let show = true;
      if (type === 'ecom')         show = vert === 'ecom';
      else if (type === 'lead_gen') show = vert === 'lead_gen';
      else if (type === 'google-only') show = hasG && !hasM;
      else if (type === 'meta-only')   show = hasM && !hasG;
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
</script>
</body>
</html>"""


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    start, end = last_7_days()
    print(f"\nHöski Dashboard Builder")
    print(f"Date range: {start} → {end}")
    print(f"Pulling data for {len(ALL_CLIENTS)} clients...\n")

    rows = collect_all(start, end)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    html = render_html(rows, start, end)
    OUTPUT_PATH.write_text(html, encoding="utf-8")

    print(f"\nDone. Dashboard written to: {OUTPUT_PATH}")
    print(f"\nTo publish:")
    print(f"  git add docs/index.html")
    print(f'  git commit -m "chore: refresh dashboard {end}"')
    print(f"  git push")


if __name__ == "__main__":
    main()
