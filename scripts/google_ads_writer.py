"""
Google Ads Writer
Purpose: Safe write/mutation operations for Google Ads accounts.
         Every operation previews changes and requires explicit approval before executing.
         All new entities (campaigns, ad groups, keywords, ads) are created PAUSED by default.

Setup:
    Requires environment variables:
        GOOGLE_ADS_DEVELOPER_TOKEN
        GOOGLE_ADS_CLIENT_ID
        GOOGLE_ADS_CLIENT_SECRET
        GOOGLE_ADS_REFRESH_TOKEN
        GOOGLE_ADS_CUSTOMER_ID  (your MCC ID)

Usage:
    python3 scripts/ads_writer.py --customer-id ACCOUNT_ID --operation OPERATION [options]

Operations:
    pause-campaign       --campaign-id ID
    enable-campaign      --campaign-id ID
    update-budget        --campaign-id ID --budget AMOUNT_IN_DOLLARS
    pause-keyword        --criterion-id ID --ad-group-id ID
    enable-keyword       --criterion-id ID --ad-group-id ID
    add-negative-keyword --campaign-id ID --keyword TEXT --match-type [EXACT|PHRASE|BROAD]
    update-keyword-bid   --criterion-id ID --ad-group-id ID --bid AMOUNT_IN_DOLLARS

Safety Rules:
    - All operations show a preview and ask for confirmation before executing.
    - New entities are always created in PAUSED status.
    - Use --dry-run to preview without any confirmation prompt (no changes made).

Changelog:
    2026-03-19  Initial version — pause/enable campaigns, update budgets,
                pause/enable keywords, add negative keywords, update keyword bids.
"""

import argparse
import os
import sys

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# ─── CLIENT ──────────────────────────────────────────────────────────────────

def build_client():
    return GoogleAdsClient.load_from_dict({
        "developer_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
        "client_id": os.environ["GOOGLE_ADS_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        "refresh_token": os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
        "login_customer_id": os.environ["GOOGLE_ADS_CUSTOMER_ID"],
        "use_proto_plus": True
    })


# ─── APPROVAL GATE ───────────────────────────────────────────────────────────

def print_preview(title, changes):
    print("\n" + "="*60)
    print(f"PREVIEW: {title}")
    print("="*60)
    for line in changes:
        print(f"  {line}")
    print("="*60)

def request_approval(dry_run):
    """Returns True if approved to proceed, False otherwise."""
    if dry_run:
        print("\n[DRY RUN] No changes made.")
        return False
    answer = input("\nApprove and apply these changes? [yes/no]: ").strip().lower()
    if answer == "yes":
        print("Approved. Executing...\n")
        return True
    else:
        print("Cancelled. No changes made.")
        return False


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def get_campaign(client, customer_id, campaign_id):
    """Fetch campaign name and current status for preview."""
    ga_service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT campaign.id, campaign.name, campaign.status, campaign_budget.amount_micros
        FROM campaign
        WHERE campaign.id = {campaign_id}
        LIMIT 1
    """
    try:
        rows = list(ga_service.search(customer_id=customer_id, query=query))
        if rows:
            c = rows[0].campaign
            b = rows[0].campaign_budget
            return {
                "name": c.name,
                "status": c.status.name,
                "budget_id": rows[0].campaign_budget.resource_name,
                "budget_daily": b.amount_micros / 1_000_000
            }
    except GoogleAdsException as ex:
        print(f"Error fetching campaign: {ex}")
    return None


def get_keyword(client, customer_id, ad_group_id, criterion_id):
    """Fetch keyword text and current status for preview."""
    ga_service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT
            campaign.name,
            ad_group.name,
            ad_group_criterion.criterion_id,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            ad_group_criterion.status,
            ad_group_criterion.cpc_bid_micros
        FROM keyword_view
        WHERE ad_group_criterion.criterion_id = {criterion_id}
          AND ad_group.id = {ad_group_id}
        LIMIT 1
    """
    try:
        rows = list(ga_service.search(customer_id=customer_id, query=query))
        if rows:
            kw = rows[0].ad_group_criterion
            return {
                "campaign": rows[0].campaign.name,
                "ad_group": rows[0].ad_group.name,
                "text": kw.keyword.text,
                "match_type": kw.keyword.match_type.name,
                "status": kw.status.name,
                "cpc_bid": kw.cpc_bid_micros / 1_000_000 if kw.cpc_bid_micros else None,
                "resource_name": kw.resource_name
            }
    except GoogleAdsException as ex:
        print(f"Error fetching keyword: {ex}")
    return None


# ─── OPERATIONS ──────────────────────────────────────────────────────────────

def pause_campaign(client, customer_id, campaign_id, dry_run):
    info = get_campaign(client, customer_id, campaign_id)
    if not info:
        print(f"Campaign {campaign_id} not found.")
        return

    print_preview("Pause Campaign", [
        f"Campaign:       {info['name']} (ID: {campaign_id})",
        f"Current status: {info['status']}",
        f"New status:     PAUSED",
    ])

    if not request_approval(dry_run):
        return

    campaign_service = client.get_service("CampaignService")
    campaign = client.get_type("Campaign")
    campaign.resource_name = campaign_service.campaign_path(customer_id, campaign_id)
    campaign.status = client.enums.CampaignStatusEnum.PAUSED

    field_mask = client.get_type("FieldMask")
    field_mask.paths.append("status")

    op = client.get_type("CampaignOperation")
    op.update.CopyFrom(campaign)
    op.update_mask.CopyFrom(field_mask)

    try:
        campaign_service.mutate_campaigns(customer_id=customer_id, operations=[op])
        print(f"Campaign '{info['name']}' paused successfully.")
    except GoogleAdsException as ex:
        print(f"Failed: {ex}")


def enable_campaign(client, customer_id, campaign_id, dry_run):
    info = get_campaign(client, customer_id, campaign_id)
    if not info:
        print(f"Campaign {campaign_id} not found.")
        return

    print_preview("Enable Campaign", [
        f"Campaign:       {info['name']} (ID: {campaign_id})",
        f"Current status: {info['status']}",
        f"New status:     ENABLED",
    ])

    if not request_approval(dry_run):
        return

    campaign_service = client.get_service("CampaignService")
    campaign = client.get_type("Campaign")
    campaign.resource_name = campaign_service.campaign_path(customer_id, campaign_id)
    campaign.status = client.enums.CampaignStatusEnum.ENABLED

    field_mask = client.get_type("FieldMask")
    field_mask.paths.append("status")

    op = client.get_type("CampaignOperation")
    op.update.CopyFrom(campaign)
    op.update_mask.CopyFrom(field_mask)

    try:
        campaign_service.mutate_campaigns(customer_id=customer_id, operations=[op])
        print(f"Campaign '{info['name']}' enabled successfully.")
    except GoogleAdsException as ex:
        print(f"Failed: {ex}")


def update_budget(client, customer_id, campaign_id, new_budget_dollars, dry_run):
    info = get_campaign(client, customer_id, campaign_id)
    if not info:
        print(f"Campaign {campaign_id} not found.")
        return

    print_preview("Update Daily Budget", [
        f"Campaign:       {info['name']} (ID: {campaign_id})",
        f"Current budget: ${info['budget_daily']:.2f}/day",
        f"New budget:     ${new_budget_dollars:.2f}/day",
        f"Change:         {'+' if new_budget_dollars >= info['budget_daily'] else ''}{new_budget_dollars - info['budget_daily']:.2f}/day",
    ])

    if not request_approval(dry_run):
        return

    budget_service = client.get_service("CampaignBudgetService")
    budget = client.get_type("CampaignBudget")
    budget.resource_name = info["budget_id"]
    budget.amount_micros = int(new_budget_dollars * 1_000_000)

    field_mask = client.get_type("FieldMask")
    field_mask.paths.append("amount_micros")

    op = client.get_type("CampaignBudgetOperation")
    op.update.CopyFrom(budget)
    op.update_mask.CopyFrom(field_mask)

    try:
        budget_service.mutate_campaign_budgets(customer_id=customer_id, operations=[op])
        print(f"Budget updated to ${new_budget_dollars:.2f}/day.")
    except GoogleAdsException as ex:
        print(f"Failed: {ex}")


def pause_keyword(client, customer_id, ad_group_id, criterion_id, dry_run):
    info = get_keyword(client, customer_id, ad_group_id, criterion_id)
    if not info:
        print(f"Keyword {criterion_id} not found.")
        return

    print_preview("Pause Keyword", [
        f"Keyword:        \"{info['text']}\" [{info['match_type']}]",
        f"Campaign:       {info['campaign']}",
        f"Ad Group:       {info['ad_group']}",
        f"Current status: {info['status']}",
        f"New status:     PAUSED",
    ])

    if not request_approval(dry_run):
        return

    criterion_service = client.get_service("AdGroupCriterionService")
    criterion = client.get_type("AdGroupCriterion")
    criterion.resource_name = info["resource_name"]
    criterion.status = client.enums.AdGroupCriterionStatusEnum.PAUSED

    field_mask = client.get_type("FieldMask")
    field_mask.paths.append("status")

    op = client.get_type("AdGroupCriterionOperation")
    op.update.CopyFrom(criterion)
    op.update_mask.CopyFrom(field_mask)

    try:
        criterion_service.mutate_ad_group_criteria(customer_id=customer_id, operations=[op])
        print(f"Keyword '{info['text']}' paused successfully.")
    except GoogleAdsException as ex:
        print(f"Failed: {ex}")


def enable_keyword(client, customer_id, ad_group_id, criterion_id, dry_run):
    info = get_keyword(client, customer_id, ad_group_id, criterion_id)
    if not info:
        print(f"Keyword {criterion_id} not found.")
        return

    print_preview("Enable Keyword", [
        f"Keyword:        \"{info['text']}\" [{info['match_type']}]",
        f"Campaign:       {info['campaign']}",
        f"Ad Group:       {info['ad_group']}",
        f"Current status: {info['status']}",
        f"New status:     ENABLED",
    ])

    if not request_approval(dry_run):
        return

    criterion_service = client.get_service("AdGroupCriterionService")
    criterion = client.get_type("AdGroupCriterion")
    criterion.resource_name = info["resource_name"]
    criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED

    field_mask = client.get_type("FieldMask")
    field_mask.paths.append("status")

    op = client.get_type("AdGroupCriterionOperation")
    op.update.CopyFrom(criterion)
    op.update_mask.CopyFrom(field_mask)

    try:
        criterion_service.mutate_ad_group_criteria(customer_id=customer_id, operations=[op])
        print(f"Keyword '{info['text']}' enabled successfully.")
    except GoogleAdsException as ex:
        print(f"Failed: {ex}")


def update_keyword_bid(client, customer_id, ad_group_id, criterion_id, bid_dollars, dry_run):
    info = get_keyword(client, customer_id, ad_group_id, criterion_id)
    if not info:
        print(f"Keyword {criterion_id} not found.")
        return

    current_bid = f"${info['cpc_bid']:.2f}" if info["cpc_bid"] else "ad group default"
    print_preview("Update Keyword Bid", [
        f"Keyword:      \"{info['text']}\" [{info['match_type']}]",
        f"Campaign:     {info['campaign']}",
        f"Ad Group:     {info['ad_group']}",
        f"Current bid:  {current_bid}",
        f"New bid:      ${bid_dollars:.2f}",
    ])

    if not request_approval(dry_run):
        return

    criterion_service = client.get_service("AdGroupCriterionService")
    criterion = client.get_type("AdGroupCriterion")
    criterion.resource_name = info["resource_name"]
    criterion.cpc_bid_micros = int(bid_dollars * 1_000_000)

    field_mask = client.get_type("FieldMask")
    field_mask.paths.append("cpc_bid_micros")

    op = client.get_type("AdGroupCriterionOperation")
    op.update.CopyFrom(criterion)
    op.update_mask.CopyFrom(field_mask)

    try:
        criterion_service.mutate_ad_group_criteria(customer_id=customer_id, operations=[op])
        print(f"Bid updated to ${bid_dollars:.2f} for keyword '{info['text']}'.")
    except GoogleAdsException as ex:
        print(f"Failed: {ex}")


def add_negative_keyword(client, customer_id, campaign_id, keyword_text, match_type_str, dry_run):
    info = get_campaign(client, customer_id, campaign_id)
    if not info:
        print(f"Campaign {campaign_id} not found.")
        return

    match_type_map = {
        "EXACT": client.enums.KeywordMatchTypeEnum.EXACT,
        "PHRASE": client.enums.KeywordMatchTypeEnum.PHRASE,
        "BROAD": client.enums.KeywordMatchTypeEnum.BROAD,
    }
    match_type = match_type_map.get(match_type_str.upper())
    if not match_type:
        print(f"Invalid match type '{match_type_str}'. Use EXACT, PHRASE, or BROAD.")
        return

    print_preview("Add Negative Keyword", [
        f"Campaign:   {info['name']} (ID: {campaign_id})",
        f"Negative:   -{keyword_text} [{match_type_str.upper()}]",
        f"Level:      Campaign-level negative",
    ])

    if not request_approval(dry_run):
        return

    criterion_service = client.get_service("CampaignCriterionService")
    campaign_service = client.get_service("CampaignService")

    criterion = client.get_type("CampaignCriterion")
    criterion.campaign = campaign_service.campaign_path(customer_id, campaign_id)
    criterion.negative = True
    criterion.keyword.text = keyword_text
    criterion.keyword.match_type = match_type

    op = client.get_type("CampaignCriterionOperation")
    op.create.CopyFrom(criterion)

    try:
        criterion_service.mutate_campaign_criteria(customer_id=customer_id, operations=[op])
        print(f"Negative keyword '-{keyword_text} [{match_type_str.upper()}]' added to '{info['name']}'.")
    except GoogleAdsException as ex:
        print(f"Failed: {ex}")


# ─── ARGS ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Google Ads Writer — safe mutations with approval gate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/ads_writer.py --customer-id 5544702166 --operation pause-campaign --campaign-id 123456
  python3 scripts/ads_writer.py --customer-id 5544702166 --operation update-budget --campaign-id 123456 --budget 75
  python3 scripts/ads_writer.py --customer-id 5544702166 --operation add-negative-keyword --campaign-id 123456 --keyword "free shipping" --match-type PHRASE
  python3 scripts/ads_writer.py --customer-id 5544702166 --operation update-keyword-bid --ad-group-id 789 --criterion-id 456 --bid 2.50
  python3 scripts/ads_writer.py --customer-id 5544702166 --operation pause-campaign --campaign-id 123456 --dry-run
        """
    )
    parser.add_argument("--customer-id", required=True, help="Google Ads account ID (no dashes)")
    parser.add_argument("--operation", required=True, choices=[
        "pause-campaign", "enable-campaign", "update-budget",
        "pause-keyword", "enable-keyword", "update-keyword-bid",
        "add-negative-keyword",
    ])
    parser.add_argument("--campaign-id", help="Campaign ID")
    parser.add_argument("--ad-group-id", help="Ad Group ID")
    parser.add_argument("--criterion-id", help="Keyword criterion ID")
    parser.add_argument("--budget", type=float, help="New daily budget in dollars")
    parser.add_argument("--bid", type=float, help="New keyword bid in dollars")
    parser.add_argument("--keyword", help="Keyword text (for adding negatives)")
    parser.add_argument("--match-type", default="EXACT", help="Match type: EXACT, PHRASE, BROAD")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    args = parser.parse_args()

    customer_id = args.customer_id.replace("-", "")
    client = build_client()

    op = args.operation

    if op == "pause-campaign":
        if not args.campaign_id:
            sys.exit("--campaign-id required for pause-campaign")
        pause_campaign(client, customer_id, args.campaign_id, args.dry_run)

    elif op == "enable-campaign":
        if not args.campaign_id:
            sys.exit("--campaign-id required for enable-campaign")
        enable_campaign(client, customer_id, args.campaign_id, args.dry_run)

    elif op == "update-budget":
        if not args.campaign_id or args.budget is None:
            sys.exit("--campaign-id and --budget required for update-budget")
        update_budget(client, customer_id, args.campaign_id, args.budget, args.dry_run)

    elif op == "pause-keyword":
        if not args.ad_group_id or not args.criterion_id:
            sys.exit("--ad-group-id and --criterion-id required for pause-keyword")
        pause_keyword(client, customer_id, args.ad_group_id, args.criterion_id, args.dry_run)

    elif op == "enable-keyword":
        if not args.ad_group_id or not args.criterion_id:
            sys.exit("--ad-group-id and --criterion-id required for enable-keyword")
        enable_keyword(client, customer_id, args.ad_group_id, args.criterion_id, args.dry_run)

    elif op == "update-keyword-bid":
        if not args.ad_group_id or not args.criterion_id or args.bid is None:
            sys.exit("--ad-group-id, --criterion-id, and --bid required for update-keyword-bid")
        update_keyword_bid(client, customer_id, args.ad_group_id, args.criterion_id, args.bid, args.dry_run)

    elif op == "add-negative-keyword":
        if not args.campaign_id or not args.keyword:
            sys.exit("--campaign-id and --keyword required for add-negative-keyword")
        add_negative_keyword(client, customer_id, args.campaign_id, args.keyword, args.match_type, args.dry_run)


if __name__ == "__main__":
    main()
