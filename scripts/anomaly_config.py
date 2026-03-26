"""
Anomaly Monitor — Configuration
Purpose: Centralised threshold configuration for anomaly_monitor.py.
         Edit these values to tune sensitivity for your account mix.

Changelog:
    2026-03-23  Initial version.
"""

# ─── CONVERSION ANOMALIES ─────────────────────────────────────────────────────

# Minimum 7-day daily conversion average required to trigger a zero-conversion
# alert. Accounts averaging below this are too low-volume to flag reliably.
CONV_ZERO_MIN_DAILY_AVG = 0.5       # ~3-4 conversions per week minimum

# If yesterday's conversions are this fraction BELOW the 7-day daily average,
# flag as CRITICAL.
CONV_DROP_THRESHOLD = 0.50          # >50% drop vs daily average

# ─── SPEND ANOMALIES ─────────────────────────────────────────────────────────

# If yesterday's total spend was above this multiple of total daily budget.
SPEND_OVERPACE_THRESHOLD = 1.20     # >120% of daily budget

# If yesterday's total spend was below this fraction of total daily budget.
# Indicates campaigns may have stopped or been accidentally paused.
SPEND_UNDERPACE_THRESHOLD = 0.20    # <20% of daily budget

# If a single campaign consumed this fraction of total account spend.
# Flags concentration risk (account dependent on one campaign).
SPEND_CONCENTRATION_THRESHOLD = 0.80    # single campaign >80% of account spend

# ─── TRAFFIC QUALITY ─────────────────────────────────────────────────────────

# WoW drop in CTR (fractional) that triggers a WARNING.
CTR_DROP_THRESHOLD = 0.30           # >30% relative WoW CTR drop

# WoW drop in Search Impression Share (absolute percentage points) for WARNING.
IS_DROP_THRESHOLD = 15.0            # >15 absolute points drop in IS

# WoW increase in average CPC (fractional) that triggers a WARNING.
CPC_SPIKE_THRESHOLD = 0.40          # >40% relative WoW CPC increase

# ─── STRUCTURAL ──────────────────────────────────────────────────────────────

# Flag active ad groups with zero impressions over this many days.
ZERO_IMPRESSION_DAYS = 7

# Minimum 30-day account spend ($) to suppress false positives on inactive accounts.
MIN_ACCOUNT_SPEND_30D = 50.0

# Maximum zero-impression ad group alerts per account (prevents flooding output
# when an entire campaign is misconfigured).
MAX_ZERO_IMPRESSION_ALERTS = 5

# ─── PER-CLIENT OVERRIDES ────────────────────────────────────────────────────
# Override any threshold for specific accounts where defaults are too noisy.
# Key = customer_id string. Unspecified accounts use defaults above.

CLIENT_OVERRIDES = {
    # Low-volume accounts: lower the min daily avg so we still catch tag breaks
    "3720173680": {"CONV_ZERO_MIN_DAILY_AVG": 0.1},    # New Norseman
    "7087867966": {"CONV_ZERO_MIN_DAILY_AVG": 0.1},    # GDM Google Ads
    "8134824884": {"CONV_ZERO_MIN_DAILY_AVG": 0.1},    # Serenity Familycare
}
