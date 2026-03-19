# Claude Code for Google Ads: Complete Setup Guide

## What is this?

You know how you can chat with ChatGPT or Claude in a browser? Claude Code is different — it runs inside your code editor (VS Code) or terminal, and it can actually **do things**. It can read files, write code, run scripts, and connect to APIs on your behalf.

This guide shows you how to connect Claude Code to the **Google Ads API** so that it becomes your PPC co-pilot. Once set up, you can have a conversation like *"pull my last 30 days of search terms and find what's wasting money"* — and Claude will actually query your Google Ads account, analyze the data, and give you a prioritized list of negatives to add. No copy-pasting spreadsheets. No exporting CSVs.

You'll also set up a workspace with agent prompts (specialist instructions for things like audits, ad copy, negative keywords) and a knowledge base (your PPC rules and frameworks) so Claude doesn't just give generic AI advice — it gives advice grounded in real PPC strategy.

**Think of it as:** a senior PPC analyst that lives inside VS Code, has direct access to your Google Ads data, knows your playbooks, and never sleeps.

---

> **Who this is for:** PPC managers, agency owners, freelancers, and in-house teams who want to use AI to work faster and smarter in Google Ads.
>
> **Time to set up:** One sitting. You'll need a Google Ads account and a few API keys.
>
> **Platform:** This guide covers macOS, Linux, and Windows. Steps are the same unless noted.

---

## Table of Contents

1. [What You'll Be Able to Do](#1-what-youll-be-able-to-do)
2. [Prerequisites](#2-prerequisites)
3. [Step 1: Install Claude Code](#step-1-install-claude-code)
4. [Step 2: Create Your Workspace](#step-2-create-your-workspace)
5. [Step 3: Set Up Google Ads API Access](#step-3-set-up-google-ads-api-access)
6. [Step 4: Install Python Dependencies](#step-4-install-python-dependencies)
7. [Step 5: Create Your CLAUDE.md](#step-5-create-your-claudemd)
8. [Step 6: Add MCP Servers (Optional but Recommended)](#step-6-add-mcp-servers-optional-but-recommended)
9. [Step 7: Add Agent Prompts](#step-7-add-agent-prompts)
10. [Step 8: Add Frameworks & Knowledge](#step-8-add-frameworks--knowledge)
11. [Step 9: Test Your Setup](#step-9-test-your-setup)
12. [Example Workflows](#example-workflows)
13. [Google Ads Scripts Library](#google-ads-scripts-library)
14. [Tips & Troubleshooting](#tips--troubleshooting)

---

## 1. What You'll Be Able to Do

Once set up, you can ask Claude things like:

- *"Pull last 30 days of campaign data and tell me what's wasting money"*
- *"Audit this account — find the top 10 things I should fix"*
- *"Write a Google Ads script that pauses keywords with zero conversions and CPC over $5"*
- *"Analyze my search terms and build a negative keyword list"*
- *"Generate 15 RSA headlines for [product/service]"*
- *"Compare my top 3 campaigns and tell me where to shift budget"*
- *"Check my conversion tracking setup for issues"*
- *"Write a weekly performance report I can send to my client"*

Claude will use the Google Ads API directly, write scripts, generate reports, and give you expert-level PPC analysis.

---

## 2. Prerequisites

Before you start, you need:

| Requirement | Where to Get It |
|---|---|
| **Claude Code** | [claude.com/download](https://claude.com/download) (requires Claude Pro, Team, or Enterprise plan) |
| **Google Ads account** | Any account — MCC or individual |
| **Google Ads API access** | Google Ads API Center (see Step 3) |
| **Python 3.10+** | [python.org](https://python.org) — or `brew install python` on Mac |
| **Node.js 18+** (optional) | For MCP servers — [nodejs.org](https://nodejs.org) |
| **VS Code** (recommended) | [code.visualstudio.com](https://code.visualstudio.com) — Claude Code has a native extension |

---

## Step 1: Install Claude Code

### Option A: VS Code Extension (Recommended)

This is the easiest way to get started and gives you a rich IDE experience.

1. Open VS Code
2. Go to Extensions (Cmd+Shift+X on Mac / Ctrl+Shift+X on Windows/Linux)
3. Search **"Claude Code"**
4. Install the **Anthropic** extension
5. Sign in with your Claude account
6. You'll see the Claude Code panel in the sidebar — this is where you'll interact with Claude

### Option B: CLI (Terminal)
```bash
# macOS/Linux
npm install -g @anthropic-ai/claude-code

# Then run from any directory
claude
```

> **Note:** The CLI is currently macOS and Linux only. Windows users should use the VS Code extension (Option A) or WSL (Windows Subsystem for Linux).

---

## Step 2: Create Your Workspace

Create a dedicated folder for your PPC work. This is where Claude will look for instructions, prompts, and scripts.

**macOS / Linux:**
```bash
mkdir -p ~/ppc-workspace
cd ~/ppc-workspace

# Create the folder structure
mkdir -p system-prompts/agents
mkdir -p system-prompts/frameworks
mkdir -p google-ads-scripts
mkdir -p scripts
mkdir -p reports
```

**Windows (PowerShell):**
```powershell
mkdir ~\ppc-workspace
cd ~\ppc-workspace

mkdir system-prompts\agents
mkdir system-prompts\frameworks
mkdir google-ads-scripts
mkdir scripts
mkdir reports
```

Your structure will look like this:

```
ppc-workspace/
├── CLAUDE.md              ← Claude's instructions (you'll create this)
├── .gitignore             ← Keeps credentials out of git
├── system-prompts/
│   ├── agents/            ← Specialist prompts (audit, ads, keywords, etc.)
│   └── frameworks/        ← PPC knowledge & playbooks
├── google-ads-scripts/    ← Google Ads scripts (JavaScript)
├── scripts/               ← Python utility scripts
└── reports/               ← Generated audit reports & exports
```

### Create a .gitignore (Important)

If you ever use git with this workspace, this prevents accidental credential leaks.

Create a file called **`.gitignore`** in your workspace root:

```
# Credentials & secrets
.env
*.json.bak
credentials.json

# Python
__pycache__/
*.pyc
venv/

# OS files
.DS_Store
Thumbs.db

# Reports (optional — remove this line if you want to track reports in git)
reports/
```

---

## Step 3: Set Up Google Ads API Access

This is the most involved step, but you only do it once.

### 3a. Get a Developer Token

1. Sign into your Google Ads MCC (or individual account)
2. Go to **Tools & Settings > API Center**
3. If you don't see API Center, you may need to create an MCC at [ads.google.com/home/tools/manager-accounts/](https://ads.google.com/home/tools/manager-accounts/)
4. Apply for **Basic Access** (this is free)
5. Copy your **Developer Token**

> **Important: API Approval Can Take Time.**
> Basic Access approval can take anywhere from a few days to a few weeks. Google reviews your application manually.
>
> **While you wait**, you can still use Claude Code for:
> - Writing Google Ads scripts (these don't need API access)
> - Generating ad copy, audit checklists, and frameworks
> - Analyzing exported data (export CSVs from the Google Ads UI)
>
> You can also apply for a **Test Account** in the API Center which gives you immediate access to a sandboxed environment to practice with the API. Test accounts can't access real campaign data, but they let you verify your code works.

### 3b. Set Up Google Cloud Console & OAuth Consent Screen

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (e.g., "PPC Claude Code")
3. **Enable the Google Ads API:**
   - Go to APIs & Services > Library
   - Search "Google Ads API" > Click **Enable**
4. **Configure the OAuth consent screen** (required before creating credentials):
   - Go to APIs & Services > **OAuth consent screen**
   - Choose **External** user type (unless you have Google Workspace, then Internal is fine)
   - Fill in the required fields: App name (e.g., "PPC Tool"), your email for support contact
   - On the **Scopes** page, click "Add or remove scopes" and add: `https://www.googleapis.com/auth/adwords`
   - Add your own Google account email as a **Test User**
   - Save and continue through the remaining screens
5. **Create OAuth credentials:**
   - Go to APIs & Services > Credentials
   - Click **Create Credentials > OAuth 2.0 Client ID**
   - Application type: **Desktop app**
   - Copy the **Client ID** and **Client Secret**

### 3c. Get a Refresh Token

Create this helper script to generate your OAuth refresh token:

**`scripts/get_google_refresh_token.py`**
```python
"""
Google Ads OAuth2 Refresh Token Generator
Run this once to get your refresh token, then store it as an environment variable.
"""

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/adwords"]

# Replace with YOUR values from Google Cloud Console
CLIENT_CONFIG = {
    "installed": {
        "client_id": "YOUR_CLIENT_ID_HERE",
        "client_secret": "YOUR_CLIENT_SECRET_HERE",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

def main():
    flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
    credentials = flow.run_local_server(port=8080)
    print(f"\n=== Your Refresh Token ===")
    print(f"{credentials.refresh_token}")
    print(f"\nAdd this to your shell profile (~/.zshrc or ~/.bashrc):")
    print(f'export GOOGLE_ADS_REFRESH_TOKEN="{credentials.refresh_token}"')

if __name__ == "__main__":
    main()
```

Run it:
```bash
pip install google-auth-oauthlib
python scripts/get_google_refresh_token.py
```

This will open a browser window — sign in with the Google account that has access to your Google Ads account. If you see a "This app isn't verified" warning, click **Advanced > Go to [app name]** — this is expected for your own personal OAuth app.

### 3d. Store Your Credentials

**macOS / Linux** — add to your shell profile (`~/.zshrc` on Mac, `~/.bashrc` on Linux):

```bash
# Google Ads API
export GOOGLE_ADS_DEVELOPER_TOKEN="your-developer-token"
export GOOGLE_ADS_CLIENT_ID="your-oauth-client-id"
export GOOGLE_ADS_CLIENT_SECRET="your-oauth-client-secret"
export GOOGLE_ADS_REFRESH_TOKEN="your-refresh-token"
export GOOGLE_ADS_CUSTOMER_ID="your-mcc-or-account-id"  # Numbers only, no dashes
```

Then reload:
```bash
source ~/.zshrc
```

**Windows** — set environment variables via PowerShell (run as Administrator):

```powershell
[System.Environment]::SetEnvironmentVariable("GOOGLE_ADS_DEVELOPER_TOKEN", "your-developer-token", "User")
[System.Environment]::SetEnvironmentVariable("GOOGLE_ADS_CLIENT_ID", "your-oauth-client-id", "User")
[System.Environment]::SetEnvironmentVariable("GOOGLE_ADS_CLIENT_SECRET", "your-oauth-client-secret", "User")
[System.Environment]::SetEnvironmentVariable("GOOGLE_ADS_REFRESH_TOKEN", "your-refresh-token", "User")
[System.Environment]::SetEnvironmentVariable("GOOGLE_ADS_CUSTOMER_ID", "your-mcc-or-account-id", "User")
```

Then restart VS Code for the variables to take effect.

> **Security Note:** Never commit these to git. They're in your system environment, not in your project folder. The `.gitignore` you created earlier adds an extra layer of safety.

---

## Step 4: Install Python Dependencies

```bash
pip install google-ads google-auth-oauthlib google-auth
```

Test your connection by running an actual query:

```bash
python3 -c "
from google.ads.googleads.client import GoogleAdsClient
import os

client = GoogleAdsClient.load_from_dict({
    'developer_token': os.environ['GOOGLE_ADS_DEVELOPER_TOKEN'],
    'client_id': os.environ['GOOGLE_ADS_CLIENT_ID'],
    'client_secret': os.environ['GOOGLE_ADS_CLIENT_SECRET'],
    'refresh_token': os.environ['GOOGLE_ADS_REFRESH_TOKEN'],
    'login_customer_id': os.environ['GOOGLE_ADS_CUSTOMER_ID'],
    'use_proto_plus': True
})

# Actually query the API to verify access
ga_service = client.get_service('GoogleAdsService')
customer_id = os.environ['GOOGLE_ADS_CUSTOMER_ID']
query = 'SELECT customer.descriptive_name FROM customer LIMIT 1'

try:
    response = ga_service.search(customer_id=customer_id, query=query)
    for row in response:
        print(f'Connected successfully! Account: {row.customer.descriptive_name}')
except Exception as e:
    print(f'Connection failed: {e}')
"
```

If you see your account name printed, you're good. If you get an error, check the troubleshooting section at the end.

---

## Step 5: Create Your CLAUDE.md

This is the most important file. It tells Claude what tools it has, how to use them, and what your setup looks like. Claude reads this automatically when you open the workspace.

Create a file called **`CLAUDE.md`** in the root of your workspace and paste in the following. Replace `YOUR_ACCOUNT_ID` with your actual Google Ads account ID (numbers only, no dashes):

````markdown
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
customer_id = "YOUR_ACCOUNT_ID"  # No dashes

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

## Workspace Structure

```
ppc-workspace/
├── CLAUDE.md              ← You are here
├── system-prompts/
│   ├── agents/            ← Specialist agent prompts
│   └── frameworks/        ← PPC knowledge base
├── google-ads-scripts/    ← Google Ads scripts (JS)
├── scripts/               ← Python utilities
└── reports/               ← Generated reports
```

## Preferences

- When writing Google Ads scripts, always include a header comment block with the script's purpose, setup instructions, and a changelog.
- Use Python with the google-ads library (gRPC) for API calls. The REST API returns 501 errors for many operations.
- Write clear, commented, production-ready code.
- When auditing, always provide specific actionable recommendations, not generic advice.
- Reference specific data (campaign names, keyword text, actual metrics) in your analysis.
````

> **Tip:** You can add more to CLAUDE.md over time. Any additional API keys, tools, or preferences you want Claude to know about — put them here. For example, add your CPA targets, ROAS goals, brand terms, or industry vertical so Claude factors them into every analysis.

---

## Step 6: Add MCP Servers (Optional but Recommended)

MCP (Model Context Protocol) servers give Claude extra capabilities like browsing websites, reading documentation, and more. These are optional but very useful.

### Where to put the MCP config

The config file location depends on how you're using Claude Code:

| Usage | Config File Location |
|---|---|
| **VS Code extension** | `.vscode/mcp.json` inside your workspace folder |
| **CLI (terminal)** | `~/.claude/mcp.json` in your home directory |
| **Both** | Create both files with the same content |

### Recommended MCPs for PPC

**For VS Code** — create **`.vscode/mcp.json`** in your workspace:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@anthropic-ai/mcp-playwright@latest"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstreamapi/context7-mcp@latest"]
    }
  }
}
```

**For CLI** — create **`~/.claude/mcp.json`** in your home directory with the same content.

| MCP | What It Does | Why It's Useful for PPC |
|-----|---|---|
| **Playwright** | Browser automation & screenshots | Audit landing pages, take screenshots, check page speed |
| **Context7** | Fetch latest library docs | Always up-to-date Google Ads API references |

### Optional MCPs (if you have the API keys)

Add these to the same config file:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@anthropic-ai/mcp-playwright@latest"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstreamapi/context7-mcp@latest"]
    },
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "your-key-here"
      }
    },
    "exa": {
      "command": "npx",
      "args": ["-y", "exa-mcp-server"],
      "env": {
        "EXA_API_KEY": "your-key-here"
      }
    }
  }
}
```

| MCP | What It Does | Why It's Useful |
|-----|---|---|
| **Firecrawl** | Converts any webpage to clean markdown | Analyze competitor landing pages, extract ad copy |
| **Exa** | AI-powered web search | Research competitors, find industry benchmarks |

### Install browser for Playwright

```bash
npx playwright install chromium
```

---

## Step 7: Add Agent Prompts

Agent prompts are specialist instructions that tell Claude HOW to do specific PPC tasks. Save these as markdown files in `system-prompts/agents/`.

When you want to use one, just tell Claude: *"Use the audit agent prompt to audit this account"* or reference it directly.

### Starter Agent: PPC Audit Agent

**`system-prompts/agents/ppc-audit-agent.md`**

````markdown
# PPC Audit Agent

You are a senior PPC strategist performing a comprehensive Google Ads account audit. Your job is to find wasted spend, missed opportunities, and quick wins.

## Audit Process

### 1. Account Overview
Pull high-level data first:
- Total spend, conversions, CPA, ROAS for last 30 days
- Campaign count, ad group count, keyword count
- Campaign types breakdown (Search, Shopping, PMax, Display, etc.)

### 2. Campaign Analysis
For each campaign:
- Is it profitable? (Compare CPA to target, or ROAS to target)
- Budget utilization: Is it limited by budget? Overspending?
- Impression share: What are we missing?

### 3. Keyword Analysis
- Keywords with spend but zero conversions (last 30+ days)
- Keywords with CPA >2x target
- Keywords with high impression share loss
- Match type distribution — over-reliance on broad?

### 4. Search Terms Review
- Irrelevant search terms consuming budget
- Recurring patterns that need negative keywords
- High-converting terms that should be added as exact match

### 5. Ad Copy Analysis
- Ad groups with fewer than 2 active RSAs
- Pinned headline/description usage (limiting optimization)
- Ad strength scores — any "Poor" or "Average"?
- Top-performing headlines and descriptions

### 6. Quality Score
- Keywords with QS below 5
- Breakdown: ad relevance, landing page experience, expected CTR
- Priority fixes (high spend + low QS = biggest opportunity)

### 7. Conversion Tracking
- Are conversions set up correctly?
- Primary vs secondary conversion actions
- Any conversion actions with zero conversions?

### 8. Quick Wins
Summarize the top 5-10 changes that would have the biggest impact, ranked by estimated savings or improvement.

## Output Format

Structure your audit as:

1. **Executive Summary** (3-5 sentences)
2. **Account Health Score** (1-10 with justification)
3. **Critical Issues** (fix immediately)
4. **High Priority** (fix this week)
5. **Medium Priority** (fix this month)
6. **Low Priority / Nice to Have**
7. **What's Working Well** (don't break these)

Always include specific numbers: campaign names, keyword text, actual spend figures, and clear recommended actions.
````

### Starter Agent: Negative Keyword Agent

**`system-prompts/agents/negative-keyword-agent.md`**

````markdown
# Negative Keyword Agent

You are a specialist in identifying wasted spend through search term analysis and building comprehensive negative keyword lists.

## Process

1. **Pull Search Terms Data**
   - Get search_term_view for the last 30-90 days
   - Include impressions, clicks, cost, conversions

2. **Identify Waste Categories**
   - Completely irrelevant terms (wrong product, wrong intent)
   - Informational queries (how to, what is, tutorial, free)
   - Competitor searches (unless running competitor campaigns)
   - Job-related searches (jobs, careers, salary, hiring)
   - DIY/self-service queries (if selling a service)
   - Wrong geographic intent
   - Wrong audience (students, kids, etc.)

3. **Build Negative Keyword Lists**
   - Group negatives by theme (brand, informational, competitor, etc.)
   - Recommend match type for each (exact or phrase match)
   - Flag any negatives that might block valuable traffic

4. **Calculate Impact**
   - Total spend on identified waste in the period
   - Projected monthly/annual savings
   - Impact on conversion rate if waste is removed

## Output Format
- Provide negatives in a ready-to-implement list
- Group by theme with explanations
- Include the spend data that justifies each negative
````

### Starter Agent: Ad Copy Agent

**`system-prompts/agents/ad-copy-agent.md`**

````markdown
# Ad Copy Agent

You are an expert Google Ads copywriter specializing in Responsive Search Ads.

## RSA Best Practices

- Write 15 unique headlines (30 chars max each)
- Write 4 unique descriptions (90 chars max each)
- Include the primary keyword in at least 3 headlines
- Include a CTA in at least 2 headlines and 2 descriptions
- Include numbers/stats where possible (e.g., "50,000+ Customers")
- Include unique selling propositions
- Vary headline structures: question, benefit, feature, urgency, social proof
- Don't repeat the same message across headlines — each should be distinct
- Consider pin positions for critical brand/offer messages

## When Writing Ads

1. Ask for or research: the product/service, target audience, key USPs, and competitor positioning
2. Write the full set of 15 headlines + 4 descriptions
3. Suggest which headlines to pin (if any) and why
4. Provide rationale for your copy choices

## Character Counts (STRICT)
- Headline: 30 characters max
- Description: 90 characters max
- Always count characters and flag any that are over the limit
````

---

## Step 8: Add Frameworks & Knowledge

Frameworks give Claude deep PPC knowledge to draw from. These go in `system-prompts/frameworks/`.

### Starter Framework: Core PPC Reasoning

**`system-prompts/frameworks/core-ppc-reasoning.md`**

````markdown
# Core PPC Reasoning Framework

## The Alignment Chain

Every element in Google Ads must align in a chain:

**Search Intent → Keyword → Ad Copy → Landing Page → Conversion Action**

If any link breaks, performance suffers. When auditing or optimizing, always check the full chain.

## Profitability Hierarchy

Evaluate everything through this lens (in order):

1. **Is it converting?** (conversion rate, conversion volume)
2. **Is it profitable?** (CPA vs target, ROAS vs target)
3. **Is it scalable?** (impression share, budget headroom)
4. **Is it efficient?** (Quality Score, CTR, wasted spend)

## Key Principles

- **Data over opinions.** Always pull the actual numbers before making recommendations.
- **Specificity over generality.** "Pause keyword X which spent $450 with 0 conversions" beats "review underperforming keywords."
- **Impact ordering.** Prioritize by: (spend at risk) × (likelihood of improvement).
- **Context matters.** A 5% CTR might be great for insurance and terrible for branded terms. Always consider the vertical and campaign type.
- **Don't break what works.** Always highlight top performers and flag them as "do not touch."

## Statistical Thresholds

Before making decisions, ensure sufficient data:

| Monthly Spend | Min. Data Period | Min. Clicks for Keyword Decisions |
|---|---|---|
| Under $5k | 60-90 days | 50+ clicks |
| $5k-$25k | 30-60 days | 30+ clicks |
| $25k-$100k | 14-30 days | 20+ clicks |
| $100k+ | 7-14 days | 15+ clicks |

Never pause a keyword with fewer than the minimum clicks unless it's clearly irrelevant.
````

---

## Step 9: Test Your Setup

Open your workspace folder in VS Code (File > Open Folder) and open the Claude Code panel. Try these commands:

### Test 1: API Connection
> *"Pull last 30 days of campaign performance data for account [YOUR-ACCOUNT-ID]. Show me a summary of spend, clicks, conversions, and CPA by campaign."*

### Test 2: Search Terms Analysis
> *"Pull search terms for the last 30 days for campaign [CAMPAIGN-NAME]. Identify any irrelevant or wasteful terms and suggest negatives."*

### Test 3: Script Generation
> *"Write a Google Ads script that identifies keywords with more than $100 spend and zero conversions in the last 30 days, and logs them to a Google Sheet."*

### Test 4: Audit
> *"Read the audit agent prompt in system-prompts/agents/ppc-audit-agent.md, then perform a full audit of account [YOUR-ACCOUNT-ID]."*

If all four work, you're fully set up.

> **Note:** If you don't have API access yet (still waiting for approval), Tests 3 and 4 (script generation and the audit structure) will still work — Claude just won't be able to pull live data for Tests 1 and 2.

---

## Example Workflows

### Weekly Account Check
```
"Pull last 7 days performance. Compare to previous 7 days.
Flag anything that changed by more than 20%.
Check search terms for new irrelevant queries.
Summarize what I need to act on this week."
```

### Monthly Audit
```
"Read the PPC audit agent prompt in system-prompts/agents/,
then perform a full audit of account [ID].
Include search terms analysis, quality score review, and ad copy assessment.
Output as a structured report and save it to reports/."
```

### Negative Keyword Mining
```
"Pull 90 days of search terms for all active Search campaigns.
Group irrelevant terms by theme.
Build negative keyword lists with match type recommendations.
Calculate total wasted spend on these terms."
```

### Ad Copy Refresh
```
"Pull ad performance for campaign [NAME].
Show me which headlines and descriptions are performing best and worst.
Write replacement copy for the underperformers.
Make sure all headlines are under 30 characters."
```

### Competitor Landing Page Analysis
```
"Use Playwright to visit [competitor-url].
Take a screenshot and analyze their landing page.
Compare their offer, messaging, and CTA to ours at [our-url].
Suggest improvements to our page."
```

### Create Draft Ads From Performance Data
```
"Pull RSA asset performance for campaign [NAME].
Show me which headlines and descriptions are winning vs losing.
Write new improved RSA ads based on the winning patterns —
add social proof, urgency, and our key USPs.
Create them as PAUSED ads in the account so I can review
before enabling. Use the Google Ads API mutate operations."
```

> This is one of the most powerful workflows: Claude analyzes what's working, generates improved ad copy within character limits, and pushes paused ads directly into your account for review. No spreadsheets, no copy-pasting into the UI.

### Full Account Audit With Actionable Report
```
"Run a complete audit of account [ID]:
1. Campaign performance with impression share analysis
2. Quality Score breakdown for all keywords
3. RSA asset performance — find winning/losing headlines
4. Device, hour-of-day, and day-of-week analysis
5. Landing page conversion rate comparison
6. Search terms analysis using the negative keyword skill
Save the full audit to reports/ as a markdown file."
```

---

## Google Ads Scripts Library

You can also ask Claude to write Google Ads scripts (JavaScript) that run inside Google Ads directly. These are useful for automation that doesn't need the API.

Some scripts to ask Claude to build for you:

| Script Idea | What It Does |
|---|---|
| **Wasted Spend Finder** | Finds keywords/search terms with spend but zero conversions |
| **Negative Keyword Gap Finder** | Identifies search terms that should be negated |
| **Budget Pacing Alert** | Warns if campaigns are over/under pacing |
| **Quality Score Tracker** | Logs QS changes to a Google Sheet over time |
| **Ad Copy Performance Matrix** | Compares headline/description performance |
| **Conversion Health Check** | Validates conversion actions are firing correctly |
| **Exact Match Enforcer** | Checks if exact match keywords are matching correctly |
| **MCC Health Dashboard** | Rolls up key metrics across multiple accounts |

Just describe what you want and Claude will write production-ready scripts with setup instructions.

---

## Tips & Troubleshooting

### Tips

1. **Build your CLAUDE.md over time.** Every time you find yourself repeating instructions, add it to CLAUDE.md so Claude remembers next time.

2. **Save useful prompts.** When a prompt works well, save it as an agent in `system-prompts/agents/` so you can reuse it.

3. **Add your targets.** Put your CPA targets, ROAS goals, and brand terms in CLAUDE.md so Claude factors them into every analysis.

4. **Use reports/ folder.** Ask Claude to save audit outputs and reports to the `reports/` folder so you build a history over time.

5. **Layer your frameworks.** The more PPC knowledge you put in `system-prompts/frameworks/`, the better Claude's analysis gets. Add your own playbooks, checklists, and rules.

6. **Ask Claude to help you build it.** Once you have the basic setup, ask Claude: *"What other agent prompts or frameworks should I add to improve my PPC workflow?"* — it'll help you expand.

### Common Issues

| Problem | Solution |
|---|---|
| **"Developer token not approved"** | Basic Access requires manual approval from Google and can take days to weeks. Use a Test Account in the meantime (API Center > Test Account). Test accounts give you immediate API access to a sandbox environment. |
| **"OAuth token expired"** | Run `python3 scripts/get_google_refresh_token.py` and update your environment variable. |
| **"This app isn't verified" warning** | This is normal for your own OAuth app. Click Advanced > Go to [app name] to continue. |
| **"REST API returns 501"** | Use the Python `google-ads` library (gRPC) instead of REST. This is a known Google limitation. |
| **"Customer not found"** | Make sure `GOOGLE_ADS_CUSTOMER_ID` is your MCC ID (no dashes), and you're passing the child account ID in queries. |
| **"Permission denied"** | The Google account used for OAuth must have admin or standard access to the Ads account. |
| **MCP servers not connecting** | Run `npx playwright install chromium` for Playwright. Ensure your config is in the right location: `.vscode/mcp.json` for VS Code, `~/.claude/mcp.json` for CLI. |
| **Environment variables not found** | Restart VS Code or your terminal after setting them. On Windows, you may need to log out and back in. |

### Expanding Your Setup

Once you're comfortable, consider adding:

- **DataForSEO API** — for SERP data, keyword research, and ranking tracking
- **Firecrawl API** — for converting competitor pages to markdown for analysis
- **Notion MCP** — for saving reports and building a knowledge base
- **Google Sheets API** — for automated reporting dashboards

Each one is just another block in your CLAUDE.md and another environment variable.

---

## Quick Reference Card

```
Workspace:       ~/ppc-workspace/
Instructions:    CLAUDE.md (Claude reads this automatically)
Agents:          system-prompts/agents/*.md
Frameworks:      system-prompts/frameworks/*.md
Scripts:         google-ads-scripts/ (JS) and scripts/ (Python)
Reports:         reports/
MCP Config:      .vscode/mcp.json (VS Code) or ~/.claude/mcp.json (CLI)
API Credentials: Environment variables (never in project files)
```

**To start:** Open the workspace folder in VS Code with the Claude Code extension installed. Claude will automatically read your CLAUDE.md and be ready to work.

---

*Built by [Stewart Dunlop](https://ppc.io) — PPC.io*
*Created for use with [Claude Code](https://claude.com/download) by Anthropic*