# Context Audit Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix four context bloat issues identified in the April 11 context audit to reduce per-session token overhead and improve autocompact behavior.

**Architecture:** Four independent config/file edits — no code, no tests. Each task is a targeted file change with a verification step. Execute in order (Task 1 has the highest impact, Task 4 is optional but worth doing).

**Tech Stack:** Claude Code settings.json, git worktree CLI, CLAUDE.md (markdown)

---

## Task 1: Add autocompact + bash output settings to global settings.json

**Files:**
- Modify: `~/.claude/settings.json`

**What and why:**
- `autocompact_percentage_override: 75` triggers compaction earlier, keeping context lean (default is ~80%)
- `BASH_MAX_OUTPUT_LENGTH: 150000` prevents Python script output from being cut off mid-stream (default truncates at ~30-50k chars)

**Current state of `~/.claude/settings.json`:**
```json
{
  "permissions": { ... },
  "statusLine": { ... },
  "enabledPlugins": { ... },
  "extraKnownMarketplaces": { ... },
  "effortLevel": "medium"
}
```

- [ ] **Step 1: Add both settings**

The file needs an `env` block added and the autocompact override at top level. After edit:

```json
{
  "env": {
    "BASH_MAX_OUTPUT_LENGTH": "150000"
  },
  "autocompact_percentage_override": 75,
  "permissions": {
    ...existing permissions...
  },
  "statusLine": {
    ...existing statusLine...
  },
  "enabledPlugins": {
    ...existing enabledPlugins...
  },
  "extraKnownMarketplaces": {
    ...existing extraKnownMarketplaces...
  },
  "effortLevel": "medium"
}
```

- [ ] **Step 2: Verify**

Run `/context` in a new session. Confirm the autocompact buffer shown is ~25% of 200k (50k tokens), not the default 33k.

---

## Task 2: Remove stale git worktree (eliminates 5 duplicate skill entries)

**What and why:**
The worktree at `.claude/worktrees/vibrant-fermi` (branch `claude/vibrant-fermi`) has its own `.claude/skills/` directory that Claude Code loads alongside the main skills. This creates 5 duplicate skill entries in /context:
- marketing-director (9t duplicate), search-terms (9t), monthly-report (7t), weekly-check (6t), new-client (5t)

The worktree is at the same commit as main (`bda1ad3`) — it's stale and not being actively developed.

**Before running: confirm there is no in-progress work in the worktree you need.**

- [ ] **Step 1: Remove the git worktree**

```bash
git worktree remove .claude/worktrees/vibrant-fermi
```

Expected output: no output (silent success) or "Removing worktrees/vibrant-fermi"

If it fails with "contains modified or untracked files", run:
```bash
git worktree remove --force .claude/worktrees/vibrant-fermi
```

- [ ] **Step 2: Verify duplicates are gone**

Run `/context` and check the skills list. The five duplicate entries (marketing-director, search-terms, monthly-report, weekly-check, new-client at 5-9 tokens each) should no longer appear.

---

## Task 3: Trim CLAUDE.md — remove 3 vague Decision Mindset rules

**Files:**
- Modify: `CLAUDE.md` (project root, lines 140-145)

**What and why:**
The Decision Mindset section has 4 bullets. Three are vague motivational statements that don't produce specific behavior — the concrete versions of these rules already exist elsewhere in the file:
- "Speed wins..." is redundant with the testing volume tables (lines 81-87, 188-197)
- "Think like an owner..." is vague with no behavioral consequence
- "Test, do not debate..." restates the $100-150/72-hour test defaults

Keep "Data over feelings" — it has a concrete follow-through: "if you cannot point to the specific data, it is a guess."

Also remove the accidental double `---` separator at line 149.

**Current Decision Mindset section (lines 140-149):**
```markdown
## Decision Mindset

- **Data over feelings.** If you cannot point to the specific data that supports a decision, it is a guess, not a decision.
- **Test, do not debate.** Opinions are free. Data costs $150 and 72 hours.
- **Think like an owner.** Every dollar spent is a dollar the client earned. Treat it that way.
- **Speed wins.** The team that tests 20 creatives a month beats the team that tests 5. Do not be reckless, but do not be slow.

---

---
```

- [ ] **Step 1: Replace the Decision Mindset section**

Replace the current section with:
```markdown
## Decision Mindset

- **Data over feelings.** If you cannot point to the specific data that supports a decision, it is a guess, not a decision.

---
```

- [ ] **Step 2: Verify**

Count lines: `wc -l CLAUDE.md`
Expected: ~362 lines (down from 367, removing 5 lines).
Check the file reads cleanly around line 140.

---

## Task 4: Move Vertical Performance Benchmarks to reference file

**Files:**
- Create: `docs/benchmarks.md`
- Modify: `CLAUDE.md` (lines 346-368)

**What and why:**
The Vertical Performance Benchmarks table (22 lines, ~500 tokens) is pure lookup data — CPL targets and CVR ranges by vertical. It doesn't change behavior on every turn; it's a reference you consult when setting targets or triaging performance. Moving it to a reference file saves ~500 tokens per session.

- [ ] **Step 1: Create `docs/benchmarks.md`**

```markdown
# Vertical Performance Benchmarks

Directional starting points for setting initial targets and triaging performance. Update as portfolio data accumulates.

| Vertical | Target CPL | Benchmark LP CVR | Show Rate Target | Lead-to-Close Target |
|---|---|---|---|---|
| DTC e-commerce | (AOV × margin) × 0.75 | 2-4% | N/A | N/A |
| General dental | $40-80 | 3-6% | 65%+ | 40-60% |
| High-ticket dental (implants) | $150-350 | 1-3% | 55-65% | 25-40% |
| Med spa / aesthetics | $30-70 | 3-5% | 65-75% | 50-65% |
| Chiropractic / functional medicine | $30-60 | 4-7% | 60-70% | 35-55% |
| Legal | $80-200 | 2-4% | 50-65% | Varies by practice area |
| Construction / home renovation | $60-150 | 2-5% | 55-65% | 20-40% |
| High-ticket retail (jewelry / furniture) | $50-120 | 1-3% | N/A | Varies |
| Plastic surgery / cosmetic surgery | $80-200 | 2-4% | 55-65% | 25-40% |
| B2B agency services | $80-200 | 2-5% | 60-70% | 20-35% |

**How to use:**
- In Week 1: document the targets you are working toward based on client unit economics and this table.
- In the weekly rhythm: flag any metric that has been below target for 2+ consecutive weeks.
- In the monthly report: show the trend — not just the current number — against these benchmarks.
- If a client's close rate is below target: the problem is not the campaigns. Surface this to the client with data and address it operationally (follow-up speed, offer, sales process) before adjusting ad spend.
```

- [ ] **Step 2: Replace the benchmarks section in CLAUDE.md**

Replace lines 346-368 (from `### Vertical Performance Benchmarks` to end of file) with:

```markdown
### Vertical Performance Benchmarks

Reference: `docs/benchmarks.md` — CPL targets, LP CVR, show rate, and lead-to-close targets by vertical.
```

- [ ] **Step 3: Verify**

`wc -l CLAUDE.md` — expected ~345 lines (down from ~362 after Task 3).
`wc -l docs/benchmarks.md` — expected ~25 lines.
Open `docs/benchmarks.md` and confirm the table renders correctly.

---

## Summary of Token Savings

| Task | What Changes | Estimated Saving |
|---|---|---|
| Task 1 | settings.json | Behavioral (autocompact + bash output) |
| Task 2 | Remove worktree | ~36 tokens/session, cleaner skill routing |
| Task 3 | Trim CLAUDE.md | ~100 tokens/session |
| Task 4 | Move benchmarks | ~500 tokens/session |
| **Total** | | **~636 tokens/session + better autocompact** |
