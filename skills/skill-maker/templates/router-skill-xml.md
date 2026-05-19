---
name: SKILL_NAME
description: |
  What the skill does broadly. Use when [trigger phrases for any sub-command].
  Also use when [edge phrasings, related terms].
---

<essential_principles>

<principle name="PRINCIPLE_NAME">
Rule that applies to ALL commands. Explain why — agents generalize from reasoning, not rigid rules.
</principle>

<principle name="ANOTHER_PRINCIPLE">
Another cross-cutting rule with reasoning.
</principle>

</essential_principles>

<intake>
## What would you like to do?

1. **Command A** — What it does
2. **Command B** — What it does

**Wait for response before proceeding.**
</intake>

<routing>
| Response | Workflow |
|----------|----------|
| 1, "keyword-a", "alt-phrase" | `references/command-a.md` |
| 2, "keyword-b", "alt-phrase" | `references/command-b.md` |
</routing>

<reference_index>

| Reference | Load when... | Path |
|-----------|-------------|------|
| command-a | Running command A | `references/command-a.md` |
| command-b | Running command B | `references/command-b.md` |
| shared-patterns | [specific condition] | `references/shared-patterns.md` |

</reference_index>

<success_criteria>

- [ ] Criterion that proves the skill completed correctly
- [ ] Another observable, verifiable outcome

</success_criteria>
