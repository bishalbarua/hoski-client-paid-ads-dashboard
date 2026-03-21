---
name: Write Approval Required
description: All Google Ads write/mutation operations require explicit user approval before executing. New entities must be created in PAUSED/DRAFT state.
type: feedback
---

All Google Ads API write operations must follow this pattern:
1. Show a clear preview/diff of what will change
2. Wait for explicit user confirmation ("yes" / "approve") before executing
3. Any NEW entity (campaign, ad group, keyword, ad, audience) must be created in PAUSED or DRAFT state so the user can review before it goes live

**Why:** User wants full control over what goes live in client accounts. Nothing should be created live or mutated without review.

**How to apply:** Every script or code path that calls a mutate() operation must show a dry-run summary first and prompt for approval. Never execute mutations silently.
