---
name: ppc-skill-factory
description: Create production-ready Claude Skills for PPC/Google Ads tasks. Triggers when user wants to build a new PPC skill, convert PPC knowledge into a shareable skill, or create Claude instructions for advertising workflows. Encodes best practices for skill structure, context gathering, guardrails, and output formatting specific to paid advertising use cases.
---

# PPC Skill Factory

Build Claude Skills for PPC professionals that produce consistently excellent, production-quality outputs.

## Why PPC Skills Need Special Care

Generic AI skills fail at PPC because:
1. **Context dependency:** Same data, different recommendations based on business model
2. **Risk of harm:** Bad negative keywords can tank an account
3. **Technical precision:** Match types, bid strategies, structure matter
4. **Domain expertise:** Patterns that seem obvious require deep PPC knowledge

This skill factory encodes battle-tested patterns from production PPC systems.

---

## Skill Architecture Principles

### 1. Context Before Analysis

**Every PPC skill MUST gather context before doing anything:**

```markdown
## Critical Context Gathering

Before analyzing, I need to understand your business:

**1. [Primary Context]**
[What I absolutely need to do this safely]

**2. [Secondary Context]**
[What improves quality significantly]

**3. [Optional Context]**
[Nice to have, with defaults if missing]
```

**Why:** A "jobs" search term is waste for a plumber but gold for a recruiter. Context prevents disasters.

### 2. Guardrails Over Rules

**Hard guardrails that NEVER break:**
- Never recommend negating brand terms
- Never suggest changes without understanding business model
- Never give high-confidence recommendations on low data
- Always flag uncertainty

**Soft guidelines that flex with context:**
- Match type recommendations
- Bid strategy suggestions
- Structure recommendations

### 3. Structured Decision Frameworks

**Replace vague guidance with decision trees:**

```markdown
| Condition | Action | Confidence |
|-----------|--------|------------|
| X + Y | Do Z | 0.9 |
| X + not Y | Do W | 0.7 |
| Not X | Ask for more info | N/A |
```

### 4. Confidence Scoring

**Every recommendation needs confidence:**

| Level | Criteria | Language |
|-------|----------|----------|
| 0.85-1.0 | Clear pattern, sufficient data | "Recommend" |
| 0.70-0.85 | Strong signal, some edge cases | "Suggest reviewing" |
| 0.50-0.70 | Limited data, context-dependent | "Consider" |
| <0.50 | Insufficient information | "Monitor" or ask questions |

### 5. Implementation-Ready Output

**Every output should answer: "What do I DO with this?"**

❌ Generic: "Improve your headlines"
✅ Specific: "Change headline from '[current]' to '[recommended]' (28 chars)"

---

## Skill Structure Template

```markdown
---
name: [skill-name]
description: [What + when to trigger + input/output summary. 2-3 sentences max.]
---

# [Skill Name]

[One paragraph explaining what this skill does and why it's valuable]

## Core Philosophy

[3-5 principles that guide this skill's approach]
[These should be specific to the task, not generic AI platitudes]

---

## Critical Context Gathering

### Required Context (Ask if not provided)

**1. [Most Critical Context]**
[What it is, why it matters, examples]

**2. [Second Critical Context]**
[What it is, why it matters, examples]

### Recommended Context

**3. [Helpful but not blocking]**
[What it is, defaults if not provided]

### Optional Context

**4. [Nice to have]**
[What it is, how it improves output]

---

## Input Format

[What the user should provide]
[Be flexible - list multiple acceptable formats]
[Note minimum requirements and ideal requirements]

---

## Analysis Framework

### [Framework Section 1]

[Structured approach to this part of the analysis]
[Tables, decision trees, or clear categorization]

### [Framework Section 2]

[Continue with each major component]
[Include scoring criteria, thresholds, logic]

---

## Output Format

[Exact structure of what you'll deliver]
[Use markdown examples showing headers, tables, formatting]
[Be specific about what goes in each section]

---

## Guardrails

❌ **NEVER** [Critical prohibition]
❌ **NEVER** [Critical prohibition]

✅ **ALWAYS** [Required behavior]
✅ **ALWAYS** [Required behavior]

---

## Edge Cases

### [Edge Case 1]
[Situation + how to handle]

### [Edge Case 2]
[Situation + how to handle]

---

## Quality Assurance

Before delivering:
- [ ] [Checkpoint 1]
- [ ] [Checkpoint 2]
- [ ] [Checkpoint 3]
```

---

## PPC-Specific Patterns

### Pattern: Negative Keyword Analysis

**Required Context:**
- Primary service keywords (what THIS campaign targets)
- Brand terms (NEVER negative)
- Services offered (protect from false positives)
- Competitor strategy (block vs allow)

**Protected Patterns (Never Auto-Negative):**
- Commercial investigation: "best [service]", "[service] reviews"
- Comparison shopping: "[service] vs [competitor]"
- Brand + service combinations
- Primary service misspellings

**Universal Exclusion Patterns:**
- Employment: jobs, careers, salary, hiring
- DIY: how to, tutorial, template, guide
- Navigation: login, account, portal

**Match Type Framework:**
| Pattern Type | Match Type | Level |
|--------------|------------|-------|
| Universal waste | Broad | Account |
| Competitor brands | Phrase | Campaign |
| Geographic mismatch | Phrase | Campaign |
| Ambiguous terms | Exact | Ad Group |

---

### Pattern: Landing Page Analysis

**Required Context:**
- Traffic source (keyword or ad)
- Target customer persona

**Core Frameworks:**
1. **3-Second Test:** What/Who/Why/How visible immediately?
2. **Message Match Score:** 1-5 scale based on ad-to-LP alignment
3. **Trust Signal Inventory:** Above/below fold presence
4. **CTA Assessment:** Primary/Secondary/Buried

**Output Structure:**
- Message match score with breakdown
- What's working (2-3 strengths)
- Quick wins (3 specific changes)
- Strategic insight (1 deeper observation)
- Mobile checklist

---

### Pattern: Account Health Check

**Required Context:**
- Performance data (campaign-level minimum)
- Time period
- Target CPA/ROAS (if available)

**Analysis Phases:**
1. **Triage:** Critical issues requiring immediate action
2. **Opportunities:** High-leverage improvements
3. **Wins:** What's working (protect these)

**Scoring:**
- Overall health: 🟢/🟡/🔴
- Campaign tiers by CPA vs target
- Impact/effort scores for recommendations

**Output Structure:**
- Executive summary (2-3 sentences)
- Critical issues (fix this week)
- Opportunities (high leverage)
- What's working (don't break)
- Priority action list (ranked)

---

### Pattern: RSA Generation

**Required Context:**
- Target keyword(s)
- Product/service description
- Proof points (critical for quality)
- CTA preference

**Headline Allocation:**
| Category | Count | Purpose |
|----------|-------|---------|
| Keyword | 2-3 | Relevance |
| Benefit | 3-4 | Value prop |
| Proof | 2-3 | Credibility |
| CTA | 2-3 | Action |
| Differentiator | 2-3 | Uniqueness |
| Urgency | 1-2 | If applicable |

**Output:**
- 15 headlines with character counts
- 4 descriptions with character counts
- Category labels for each
- Testing recommendations

---

### Pattern: Competitor Analysis

**Required Context:**
- Your URL (for baseline)
- Competitor URLs or industry for search

**Analysis Per Competitor:**
1. Positioning statement
2. Messaging angles (primary + secondary)
3. Proof points inventory
4. Differentiation claims
5. Trust signals
6. CTA strategy

**Synthesis:**
- Message frequency matrix
- Gap analysis (critical/notable/white space)
- Positioning map
- Specific recommendations

---

## Quality Standards

### What Makes a Skill "Production-Ready"

**Completeness:**
- [ ] Context gathering covers all critical needs
- [ ] Frameworks handle common and edge cases
- [ ] Output is implementation-ready
- [ ] Guardrails prevent harmful recommendations

**Specificity:**
- [ ] Tables with clear criteria, not vague guidance
- [ ] Concrete examples for each pattern
- [ ] Exact thresholds where applicable
- [ ] Template outputs showing exact format

**Consistency:**
- [ ] Same input → same quality output
- [ ] Confidence scoring applied uniformly
- [ ] Guardrails applied without exception

**Depth:**
- [ ] Reflects real PPC expertise, not generic advice
- [ ] Handles nuance and edge cases
- [ ] Educational value embedded in structure

---

## Anti-Patterns to Avoid

❌ **Vague guidance:** "Use relevant keywords"
→ ✅ Provide specific criteria and examples

❌ **Missing context handling:** Assuming what user didn't provide
→ ✅ Ask for critical context, document defaults for optional

❌ **Generic best practices:** "Follow Google's recommendations"
→ ✅ Encode actual decision logic with trade-offs

❌ **Over-specified JSON:** Complex schemas for human-readable output
→ ✅ Clean markdown tables and structured text

❌ **No guardrails:** Recommendations that could harm account
→ ✅ Explicit protection for brand, services, high-intent terms

❌ **Unbounded scope:** Skill tries to do everything
→ ✅ Focused scope with clear boundaries

---

## Testing Your Skill

Before releasing:

1. **Run 3+ real examples** with different contexts
2. **Test edge cases:** Missing data, unusual industries, edge situations
3. **Verify guardrails:** Try to make it recommend something harmful
4. **Check output quality:** Is it actually useful and specific?
5. **Validate consistency:** Same input, same quality across runs
