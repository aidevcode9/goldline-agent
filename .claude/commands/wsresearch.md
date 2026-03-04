---
description: Research before implementing - gather context before any code is written
---

# Research Before Implementing

> **Role:** Investigator that gathers context before any code is written. Prevents "code first, understand later" mistakes.

## Trigger

- Before `/wsstart`
- When `/wsorchestrate` routes here
- User says "research [topic]" or "what do I need to know for..."

---

## Protocol

### Step 1: Understand the Task

```bash
# Read context
1. STATUS.md → What's being worked on
2. CLAUDE.md → Project conventions and red flags
```

---

### Step 2: Check Existing Code

```bash
# Search for relevant patterns
1. src/agent.py → Core logic, system prompt, tools
2. src/cli.py → CLI presentation
3. src/config.py → Branding constants
4. knowledge_base/documents/ → Policy content
5. inventory/seed_inventory.py → DB schema
```

**Look for:**
- Similar implementations to copy from
- Shared utilities to reuse
- Naming conventions to follow

---

### Step 3: Check Configuration

```bash
# What config is needed?
1. src/config.py → Existing constants
2. .env.example → Environment variables
3. pyproject.toml → Dependencies
```

---

### Step 4: Identify Risks

Consider:
- [ ] Does this touch the system prompt? Needs careful testing
- [ ] Does this change tool definitions? May affect agent behavior
- [ ] Does this modify knowledge base docs? Embeddings need regeneration
- [ ] Does this change the DB schema? Need to update seed_inventory.py
- [ ] Does this affect LangSmith tracing? Verify traces still work

---

## Output Format

```markdown
## Research: [Task Title]

### What Needs to Change
| File | Action | Purpose |
|------|--------|---------|
| `src/agent.py` | Modify | [reason] |

### Patterns to Follow
- [pattern from existing code]

### Risks
1. **Risk:** [description]
   **Mitigation:** [approach]

### Implementation Approach
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Environment Variables (if needed)
```bash
NEW_VAR=value
```

---

**Ready for /wsstart?** [Y/n]
```

---

## Invariants

1. **Research before code** — Never skip this step
2. **Document unknowns** — If something is unclear, flag it
3. **Check what exists** — Don't reinvent what's already there
4. **Output is approval gate** — Don't proceed to /wsstart without "Ready? Y"
