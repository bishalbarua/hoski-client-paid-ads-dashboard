# PPC Workspace

## Google Ads API

**Access Level:** Basic (production approved)
**Credentials:** Stored in environment variables

### Python Usage

```python
from google.ads.googleads.client import GoogleAdsClient
import os

client = GoogleAdsClient.load_from_dict({
    "developer_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
    "client_id": os.environ["GOOGLE_ADS_CLIENT_ID"],
    "client_secret": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
    "refresh_token": os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
    "login_customer_id": os.environ["GOOGLE_ADS_CUSTOMER_ID"],
    "use_proto_plus": True
})

# Query any account under your MCC
ga_service = client.get_service("GoogleAdsService")
customer_id = "7709532223"  # Hoski client account (under MCC 4781259815)

query = """
    SELECT campaign.id, campaign.name, metrics.impressions, metrics.clicks, metrics.cost_micros
    FROM campaign
    WHERE segments.date DURING LAST_30_DAYS
    ORDER BY metrics.impressions DESC
"""
response = ga_service.search(customer_id=customer_id, query=query)
```

### Common GAQL Queries

```sql
-- Campaign performance
SELECT campaign.name, metrics.impressions, metrics.clicks, metrics.cost_micros,
       metrics.conversions, metrics.conversions_value
FROM campaign
WHERE segments.date DURING LAST_30_DAYS

-- Search terms report
SELECT search_term_view.search_term, metrics.impressions, metrics.clicks,
       metrics.cost_micros, metrics.conversions
FROM search_term_view
WHERE segments.date DURING LAST_30_DAYS

-- Keyword performance
SELECT ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
       metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions
FROM keyword_view
WHERE segments.date DURING LAST_30_DAYS

-- Ad copy performance
SELECT ad_group_ad.ad.responsive_search_ad.headlines,
       ad_group_ad.ad.responsive_search_ad.descriptions,
       metrics.impressions, metrics.clicks, metrics.conversions
FROM ad_group_ad
WHERE segments.date DURING LAST_30_DAYS

-- Quality Score
SELECT ad_group_criterion.keyword.text,
       ad_group_criterion.quality_info.quality_score,
       ad_group_criterion.quality_info.creative_quality_score,
       ad_group_criterion.quality_info.post_click_quality_score,
       ad_group_criterion.quality_info.search_predicted_ctr
FROM keyword_view
WHERE ad_group_criterion.quality_info.quality_score IS NOT NULL
```

### Token Refresh

If OAuth token expires, run:
```bash
python3 scripts/get_google_refresh_token.py
```
Then update GOOGLE_ADS_REFRESH_TOKEN in your environment variables.

## Client Accounts (MCC: 4781259815)

When the user references a client by name, look up the ID here and use it in API queries.

| Client Name | Account ID |
|---|---|
| Anand Desai Law Firm | 5865660247 |
| Dentiste | 3857223862 |
| Estate Jewelry Priced Right | 7709532223 |
| FaBesthetics | 9304117954 |
| GDM Google Ads | 7087867966 |
| Hoski.ca | 5544702166 |
| New Norseman | 3720173680 |
| Park Road Custom Furniture and Decor | 7228467515 |
| Serenity Familycare | 8134824884 |
| Synergy Spine & Nerve Center | 7628667762 |
| Texas FHC | 8159668041 |
| Voit Dental (1) | 5216656756 |
| Voit Dental (2) | 5907367258 |

## Workspace Structure

```
Google Ads Manager/
├── CLAUDE.md              ← You are here
├── requirements.txt       ← Python dependencies
├── .env.example           ← Environment variable template
├── system-prompts/
│   ├── agents/            ← Specialist agent prompts
│   └── frameworks/        ← PPC knowledge base
├── google-ads-scripts/    ← Google Ads scripts (JS)
├── scripts/               ← Python utilities
│   ├── full_audit.py      ← Full account audit (any client)
│   └── get_google_refresh_token.py
├── clients/               ← Per-client notes, reports, analysis, data
└── reports/               ← Generated reports
```

## Skills

All skills live in `.claude/skills/`. Invoke by describing the task — Claude will route to the right skill automatically.

### PPC Analysis & Strategy

| Skill | Invoke When |
|---|---|
| `/new-client` | Full onboarding for a new client — intake questions, existing account audit, creates client workspace + populated client-info.md, pre-launch checklist, first 30-day plan, kickoff note |
| `/monthly-report` | Full monthly client report — pulls 30-day API data, builds internal analysis, generates polished client-facing report in business language, saves to clients/[client]/reports/ |
| `/ads-strategy-architect` | Given a client URL, build a full Google Ads + Meta launch strategy with campaign structure, audiences, and landing page prescriptions |
| `/keyword-research` | Build keyword lists from scratch for new campaigns — seed generation, intent classification, ad group organization, match type assignment, and starter negatives. Use when launching a campaign or expanding into a new service line |
| `/conversion-tracking-audit` | Deep audit of all conversion actions in an account — tag health, primary/secondary designation, double-counting detection, attribution windows, value tracking. Run before any bid strategy changes or when conversion data looks wrong |
| `/weekly-check` | Monday morning operational sweep for one client — WoW performance, pacing, tracking health, disapprovals, bid strategy signals, action list + client status note |
| `/ppc-account-health-check` | Paste or upload campaign data for a traffic-light health assessment and prioritized fix list |
| `/campaign-scaling-expert` | Identify which campaigns to scale, restructure, or pause with a ranked P1/P2/P3 action plan |
| `/pmax-shopping-analyzer` | Deep audit of Performance Max and Standard Shopping campaigns — asset group health, channel distribution, brand cannibalization, feed quality, product groups, PMax vs. Search/Shopping conflict, learning period status |
| `/facebook-ads-performance-analyzer` | Audit Meta Ads account for creative fatigue, pixel issues, audience saturation, and bid strategy problems |
| `/search-terms` | Weekly search terms sweep — negatives to add, new keyword opportunities, match type promotions, and ad group segmentation signals in one pass |
| `/negative-keyword-analyzer` | Deep one-time cleanup of a large search terms export — grouped negative recommendations with match types and confidence scores |
| `/landing-page-quick-audit` | Review a landing page URL for message match, CTA quality, trust signals, and 3 quick-win improvements |
| `/competitor-messaging-analysis` | Research competitors' positioning, proof points, and messaging gaps to sharpen ad copy differentiation |
| `/ad-copy-testing-analyzer` | Analyze RSA asset performance — BEST/GOOD/LOW/LEARNING labels, copy angle patterns, specific swap recommendations with replacement copy, structural issues (over-pinning, low variety). Run after ads have 30+ days of data |
| `/rsa-headline-generator` | Generate 15 RSA headlines + 4 descriptions from a keyword, service description, and proof points |
| `/marketing-paid-advertising` | Reference framework for multi-platform strategy: bidding, budget allocation, unit economics, attribution |

### Prompt & Skill Building

| Skill | Invoke When |
|---|---|
| `/ppc-strategic-prompt-builder` | Build a high-quality PPC analysis prompt — auto-gathers context from URLs or data, asks minimal questions |
| `/ppc-skill-factory` | Create a new production-ready PPC skill with proper context gathering, guardrails, and output format |

### Inbox & Lead Generation

| Skill | Invoke When |
|---|---|
| `/gmail-inbox` | Check email, label/archive in bulk, manage Gmail across accounts |
| `/gmail-label` | AI triage of inbox into Action Required / Waiting On / Reference using parallel subagents |

```bash
# Check unread emails
python3 .claude/skills/gmail-inbox/scripts/gmail_unified.py --query "is:unread" --limit 50

# Label and archive Google Ads notifications
python3 .claude/skills/gmail-inbox/scripts/gmail_unified.py \
  --query "from:googleads@google.com" --label "Google Ads" --archive

# Full triage flow (fetch → classify → apply)
python3 .claude/skills/gmail-label/scripts/gmail_label_fetch.py --account main --limit 100 --output .tmp/emails.json
python3 .claude/skills/gmail-label/scripts/gmail_label_split.py --input .tmp/emails.json --chunks 10 --output-dir .tmp/chunks
python3 .claude/skills/gmail-label/scripts/gmail_label_apply.py --account main --input .tmp/labels.json
```

## Preferences

- When writing Google Ads scripts, always include a header comment block with the script's purpose, setup instructions, and a changelog.
- Use Python with the google-ads library (gRPC) for API calls. The REST API returns 501 errors for many operations.
- Write clear, commented, production-ready code.
- When auditing, always provide specific actionable recommendations, not generic advice.
- Reference specific data (campaign names, keyword text, actual metrics) in your analysis.
