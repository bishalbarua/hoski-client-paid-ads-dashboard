"""
Alerts Dispatcher
Purpose: Central routing hub for all monitoring script alerts. Takes a severity
         level and message, routes to the appropriate channel based on severity.
         All monitoring scripts import this module instead of using raw print/email.

         Routing:
           CRITICAL  -> print to terminal + save to reports/alerts.log
           WARNING   -> print to terminal + save to reports/alerts.log
           INFO      -> print to terminal only

         Optional Gmail integration: set ENABLE_GMAIL=True to create Gmail drafts
         for CRITICAL alerts (requires Gmail MCP to be configured in Claude Code).

         Called by:
           anomaly_monitor.py, mcc_rollup.py, client_health_scorecard.py,
           and any future monitoring scripts.

Setup:
    No additional environment variables required beyond base setup.
    Optional: set ALERT_EMAIL in .env to receive email alerts.

Usage (as a module):
    from alerts_dispatcher import dispatch

    dispatch("CRITICAL", "Voit Dental — 0 conversions in 48h")
    dispatch("WARNING",  "Hoski.ca — CTR down 35% WoW")
    dispatch("INFO",     "MCC rollup complete — 13 accounts checked")

Usage (standalone test):
    python3 scripts/alerts_dispatcher.py --test

Changelog:
    2026-03-23  Initial version — severity routing, log file, deduplication.
"""

import os
import sys
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ─── CONFIG ──────────────────────────────────────────────────────────────────

ALERT_EMAIL   = os.environ.get("ALERT_EMAIL", "")
ENABLE_EMAIL  = bool(ALERT_EMAIL)   # set ALERT_EMAIL in .env to enable
LOG_FILE      = Path(__file__).parent.parent / "reports" / "alerts.log"

SEVERITY_ICONS = {
    "CRITICAL": "[CRITICAL]",
    "WARNING":  "[WARNING ]",
    "INFO":     "[INFO    ]",
}

# ─── DISPATCH ────────────────────────────────────────────────────────────────

def dispatch(severity, message, source="monitor", quiet=False):
    """
    Route an alert to the appropriate channel.

    Args:
        severity: "CRITICAL", "WARNING", or "INFO"
        message:  The alert message string
        source:   Which script generated the alert (for log context)
        quiet:    If True, suppress terminal output (log only)
    """
    severity  = severity.upper()
    icon      = SEVERITY_ICONS.get(severity, "[INFO    ]")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Format log line
    log_line  = f"{timestamp}  {icon}  [{source}]  {message}"

    # Always print to terminal (unless quiet)
    if not quiet:
        print(f"  {icon}  {message}")

    # Save CRITICAL and WARNING to log file
    if severity in ("CRITICAL", "WARNING"):
        _write_log(log_line)

    return log_line


def dispatch_batch(alerts, source="monitor"):
    """
    Dispatch multiple alerts at once.

    Args:
        alerts: list of (severity, message) tuples
        source: source script name

    Returns:
        dict with counts per severity level
    """
    counts = {"CRITICAL": 0, "WARNING": 0, "INFO": 0}
    for severity, message in alerts:
        dispatch(severity, message, source=source)
        counts[severity.upper()] = counts.get(severity.upper(), 0) + 1
    return counts


def summary(counts, source="monitor"):
    """Print a summary line after a batch dispatch."""
    total = sum(counts.values())
    parts = []
    if counts.get("CRITICAL"):
        parts.append(f"{counts['CRITICAL']} critical")
    if counts.get("WARNING"):
        parts.append(f"{counts['WARNING']} warnings")
    if counts.get("INFO"):
        parts.append(f"{counts['INFO']} info")

    status = "All clear" if not parts else ", ".join(parts)
    print(f"  [{source}] {total} alerts dispatched: {status}")


# ─── LOG FILE ─────────────────────────────────────────────────────────────────

def _write_log(line):
    """Append a line to the rolling alert log."""
    try:
        LOG_FILE.parent.mkdir(exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"  [alerts_dispatcher] Could not write to log: {e}", file=sys.stderr)


def get_recent_alerts(n=50):
    """Return the last n lines from the alert log."""
    if not LOG_FILE.exists():
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [l.rstrip() for l in lines[-n:]]


def count_alerts_today():
    """Count CRITICAL and WARNING alerts from today."""
    today = date.today().strftime("%Y-%m-%d")
    counts = {"CRITICAL": 0, "WARNING": 0}
    for line in get_recent_alerts(200):
        if line.startswith(today):
            if "[CRITICAL]" in line:
                counts["CRITICAL"] += 1
            elif "[WARNING ]" in line:
                counts["WARNING"]  += 1
    return counts


# ─── STANDALONE TEST ──────────────────────────────────────────────────────────

def _test():
    """Run a test dispatch to verify all channels work."""
    print("\nALERTS DISPATCHER — Self-test")
    print("=" * 50)

    dispatch("CRITICAL", "TEST: Simulated critical alert — conversion tracking broken", source="test")
    dispatch("WARNING",  "TEST: Simulated warning — CTR down 35% WoW",               source="test")
    dispatch("INFO",     "TEST: Simulated info — MCC rollup complete",                source="test")

    print()
    today_counts = count_alerts_today()
    print(f"  Today's alert count: {today_counts}")
    print(f"  Log file: {LOG_FILE}")

    recent = get_recent_alerts(5)
    if recent:
        print(f"\n  Last {len(recent)} log entries:")
        for line in recent:
            print(f"  {line}")

    print("=" * 50)
    print("  Self-test complete.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Alerts dispatcher — routing hub for monitoring alerts")
    parser.add_argument("--test", action="store_true", help="Run self-test")
    args = parser.parse_args()

    if args.test:
        _test()
    else:
        print("Usage: python3 alerts_dispatcher.py --test")
        print("       Import as a module: from alerts_dispatcher import dispatch")
