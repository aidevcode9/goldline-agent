---
description: Adversarial code review for AI failure modes
---

Review this code as a skeptic. Focus on AI-specific failure modes.

You are reviewing code for an AI customer support agent. Be adversarial.

## 1. Failure Modes

Check each and report:
- [ ] **Empty retrieval:** What happens when no knowledge base docs match?
- [ ] **No DB results:** What happens when a product query returns nothing?
- [ ] **LLM timeout:** Does it return an error or hang?
- [ ] **Malformed input:** What happens with empty queries, special characters?
- [ ] **Token limits exceeded:** What happens with very long conversation history?

## 2. Data Leakage

Check each and report:
- [ ] **Stock quantities:** Does the agent ever leak exact stock numbers? (violates policy)
- [ ] **SQL injection:** Could a user craft input that causes harmful SQL execution?
- [ ] **API keys:** Are keys properly in .env and gitignored?
- [ ] **Error messages:** Do errors reveal internal structure?

## 3. Agent Behavior

Check each and report:
- [ ] **Tool selection:** Does the agent pick the right tool for each question type?
- [ ] **Hallucination:** Could the agent invent products or policies not in the data?
- [ ] **Brand consistency:** Does it always use GoldLine branding, never OfficeFlow?
- [ ] **Scope boundaries:** Does it correctly refuse out-of-scope requests?

## 4. Knowledge Base

Check each and report:
- [ ] **Embedding staleness:** What happens if docs change but embeddings don't regenerate?
- [ ] **Missing docs:** What if a knowledge base file is deleted?
- [ ] **Relevance scores:** Are low-relevance results filtered or do they confuse the agent?

## Output Format

For each issue found:

```
CRITICAL: [description]
   Location: [file:line]
   Risk: [what could go wrong]
   Fix: [how to fix]

HIGH: [description]
   Location: [file:line]
   Risk: [what could go wrong]
   Fix: [how to fix]

LOW: [description]
   Location: [file:line]
   Suggestion: [improvement]
```

## Summary

At the end, provide:
- Total issues: X critical, Y high, Z low
- Recommendation: BLOCK / APPROVE WITH FIXES / APPROVE
