---
description: Orchestrate work session - routes to right workflows
---

# Orchestrate Work Session

> **Role:** Senior Technical Project Manager that follows the task list, batches work, and routes to the right workflows.

## Trigger

User says something like:
- "Let's work on [feature]"
- "What should I work on?"
- "Continue where we left off"
- Any ambiguous development request

---

## Protocol

### Step 1: Assess Current State

```bash
# Read project state
1. STATUS.md → Current Now, Next, Blocked
2. CLAUDE.md → Project context and conventions
```

**Output:** Brief status summary (3-5 lines max)

---

### Step 2: Determine Work Scope

**If user specified a task:**
- Validate it makes sense given current state
- Check dependencies

**If user said "continue" or "what's next":**
- Pick next items from "Next" in STATUS.md
- Batch related tasks (max 3 per session)

---

### Step 3: Create Session Plan

Present a numbered plan:

```markdown
## Session Plan

**Tasks:** [list]

### Batch 1: [Title]
1. /wsresearch → Understand patterns
2. /wsstart → Plan + implement
3. /wsverify → Lint + imports + smoke test
4. /wsskeptic → Adversarial review

**After all batches:**
- /wsstatus → Update STATUS.md
- /wscommit → Commit with references

Approve this plan? [Y/n]
```

---

### Step 4: Execute (After Approval)

For each task in the batch:

```
1. /wsresearch        → Understand before coding
2. /wsstart           → Plan + implement
3. /wsverify          → Quality gates
4. /wsskeptic         → Adversarial review
```

**Between tasks:**
- Commit working code (don't wait for all)
- Check if blocked → stop and report

**After all tasks:**
- /wsstatus → Update STATUS.md
- /wscommit → Push all changes
- Summary of what shipped
