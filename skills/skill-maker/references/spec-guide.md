# Agent Skills Specification Guide

Full spec: https://agentskills.io/specification

## Directory Structure

```
skill-name/
├── SKILL.md          # Required: YAML frontmatter + markdown instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation loaded on demand
├── assets/           # Optional: templates, icons, fonts
└── ...               # Any additional files or directories
```

## SKILL.md Format

### Frontmatter (required)

```yaml
---
name: skill-name
description: What the skill does. Use when [triggers].
---
```

| Field         | Required | Constraints                                                    |
|---------------|----------|----------------------------------------------------------------|
| name          | Yes      | Max 64 chars. Lowercase, numbers, hyphens. No leading/trailing hyphens. |
| description   | Yes      | Max 1024 chars. Non-empty. What it does + when to use it.      |
| license       | No       | License name or reference to bundled license file.             |
| compatibility | No       | Max 500 chars. Environment requirements.                       |
| metadata      | No       | Arbitrary key-value mapping.                                   |
| allowed-tools | No       | Space-separated string of pre-approved tools. (Experimental)   |

### Body (markdown instructions)

Everything after the frontmatter closing `---` is the skill's instructions. This is loaded into the agent's context when the skill activates.

## Progressive Disclosure

Three loading levels:

1. **Metadata** (~100 tokens): `name` + `description` loaded at startup for ALL skills
2. **Instructions** (< 5000 tokens recommended): Full SKILL.md body loaded on activation
3. **Resources** (as needed): Files in `scripts/`, `references/`, `assets/` loaded only when required

This means:
- Keep SKILL.md body concise — it competes for attention with everything else in context
- Move domain-specific deep-dives into `references/` files
- Tell the agent exactly when to load each reference: "Read `references/aws.md` if deploying to AWS"
- Scripts can execute without being loaded into context

## Scoping

A skill should encapsulate a coherent unit of work that composes well with other skills.

- **Too narrow**: Forces multiple skills to load for a single task, risking overhead and conflicts
- **Too broad**: Hard to activate precisely — description can't distinguish when to trigger
- **Right-sized**: One task domain, clear boundaries, natural entry and exit points

## Spending Context Wisely

Every token in your skill competes with everything else in the agent's context window.

- Aim for moderate detail — enough to guide, not so much that the agent drowns
- Use references for depth, SKILL.md for workflow
- Don't repeat information the agent already knows from training data
- Don't include information that's only relevant in rare edge cases — put that in references

## Calibrating Control

Match the level of control to the task:

- **Implicit guidance**: Describe what good output looks like and let the agent figure out how
- **Explicit guardrails**: Step-by-step checklists for multi-step workflows where order matters
- **Templates**: Exact output formats when the structure is non-negotiable
- **Gotchas sections**: Common mistakes the agent should avoid

Use explicit control for high-stakes, multi-step, or error-prone tasks. Use implicit guidance for creative or exploratory tasks.

## Reference Architecture

### The consumer is an agent

Every feature in the skill must be usable by an agent with no browser, no GUI, and no interactive prompts.

- Do not reference browser-only tools (Postman, Swagger UI, API consoles, OAuth login pages)
- Do not include resources that require a human to visually browse or click
- Ask: "Can the agent use this in a `bash` or `read` tool call?" If no, cut it.

### Each reference must be independently loadable

An agent should be able to load any single reference file and use it without being forced to load another.

**Anti-pattern (transitive loading):** Shared setup (auth, config, constants) is embedded in one reference file. Other files depend on it, forcing the agent to load an unrelated file just to get the shared setup.

**Correct pattern:** Extract shared setup into its own reference file. Consumer files point to it and assume its variables/context are set. The agent loads only what it needs.

Signs of transitive loading:
- Loading file A requires loading file B first
- The same snippet appears in 2+ reference files
- Updating a value requires editing multiple files
- Two files explain the same concept with slightly different wording

### Error handling belongs with the tool that produces the error

Don't centralize all error handling in SKILL.md. Errors from the primary tool belong in SKILL.md. Errors from tools documented in reference files belong in those reference files — that's where the agent will be when it encounters them.

### Decision tables for multi-approach skills

When a skill offers multiple ways to accomplish similar tasks (CLI, API, library, etc.), include a decision table so the agent picks the right approach. Without one, the agent defaults to whatever it loaded most recently.

- Put a routing table in SKILL.md that points to the correct reference
- Each reference file explains when to use *it* vs alternatives
- Default to the simplest approach — escalate only when it can't handle the task

## Best Practices

Full guide: https://agentskills.io/skill-creation/best-practices

- Start from real expertise — not LLM-generated content
- Write in imperative form: "Run the command" not "You should run the command"
- Include concrete examples with input → output
- Define output formats with templates when structure matters
- Add gotchas for common mistakes
- Use checklists for multi-step workflows with validation gates
- Organize by variant when supporting multiple domains (e.g., `references/aws.md`, `references/gcp.md`)
