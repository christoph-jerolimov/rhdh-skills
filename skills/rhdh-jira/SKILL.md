---
name: rhdh-jira
description: |
  Interacts with RHDH Jira projects (RHIDP, RHDHPLAN, RHDHBUGS, RHDHSUPP) using the Atlassian CLI (acli), with REST API and GraphQL fallback for custom field updates and complex queries. Use when the user needs to search, create, view, edit, transition, comment on, or link Jira issues for Red Hat Developer Hub. Also use when the user asks about Jira workflows, exit criteria, issue templates, custom fields, boards, sprints, JQL queries, or Jira API schema discovery. Trigger when the user mentions Jira issue keys like RHIDP-1234, RHDHPLAN-567, RHDHBUGS-890, or any RHDH project key. Also trigger for support case bug filing, feature request creation, release planning, or acli setup and installation.
compatibility: "acli (Atlassian CLI) on PATH. Python 3 for scripts. Windows, macOS, Linux."
---

# RHDH Jira

Foundational skill for interacting with RHDH's Jira instance via the Atlassian CLI (`acli`). Covers all four active projects, issue types, workflows, custom fields, and JQL patterns.

## Prerequisites

Run `scripts/setup.py` to verify everything is configured:

```bash
python scripts/setup.py
```

The script checks:
1. `acli` binary on PATH
2. Jira API token auth configured (`~/.config/acli/jira_config.yaml`)
3. `.jira-token` file next to `acli` executable (for REST API fallback)
4. Smoke test against `redhat.atlassian.net`

If `acli` is not installed, download from [Atlassian CLI](https://developer.atlassian.com/cloud/acli/) and follow the [Getting Started guide](https://developer.atlassian.com/cloud/acli/guides/how-to-get-started/) for installation and authentication setup. Use API token authentication, not OAuth — OAuth sessions expire and `acli auth status` gives false negatives with token auth (see Gotchas).

### REST/GraphQL capability gate

Before attempting any REST API or GraphQL call:
1. Run `python scripts/setup.py --json` and check `token_file_found`
2. If missing, state: "REST API/GraphQL fallback unavailable — `.jira-token` not configured. Run `setup.py` for instructions." Continue with acli-only workflow.
3. If the user needs REST/GraphQL, load `references/auth.md` for setup instructions

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/setup.py` | Verify acli install + auth. Run with `--json` for structured output. |
| `scripts/parse_issues.py` | Flatten, enrich, and filter acli JSON output. Solves the core problem: `acli search --json` can't return custom fields (team, story points, sprint). Pipe search results in, get clean data out. Use `--enrich` to fetch full fields, `-f team="X"` to filter by team. |

## Projects

| Key | Purpose | Issue Types |
|-----|---------|-------------|
| RHIDP | Engineering work | Epic, Story, Task, Sub-task, Vulnerability |
| RHDHPLAN | Program planning | Feature, Outcome, Feature Request, Sub-task |
| RHDHBUGS | Product defects | Bug, Sub-task |
| RHDHSUPP | Support-engineering interactions | Bug |

RHDHPAI (Plugins and AI) is **archived** — JQL queries against it will fail.

### Issue type selection

- **Story** — end-user facing work (API, UI changes)
- **Task** — not end-user facing (tests, CI/CD, refactoring, code organization)
- **Epic** — collection of Stories/Tasks toward a deliverable
- **Feature** — program-level planning item in RHDHPLAN
- **Bug** — product defect (RHDHBUGS) or support case tracking (RHDHSUPP)
- **Sub-task** — child of any issue type above
- **Vulnerability** — CVE tracking in RHIDP (Product Security)

## Reference Files

Load only what the current task requires.

| File | Load when... |
|------|-------------|
| `references/acli-commands.md` | Running an acli command you haven't used before, or hitting unexpected flag behavior. Quick reference for syntax, flag differences, and output formats. |
| `references/fields.md` | Need to know a field name, custom field ID, accepted values, or label conventions. Custom fields, labels, link types, components, priorities. |
| `references/workflows.md` | Transitioning issues, checking exit criteria, or verifying readiness for the next status. |
| `references/templates.md` | Creating new issues. Also load `references/workflows.md` for required fields at entry status. |
| `references/support.md` | Handling support cases, filing bugs from customer cases, or creating feature requests from support. |
| `references/jql-patterns.md` | Building a JQL query, finding a board ID, or looking up sprint information. JQL cookbook with 23+ tested queries. |
| `references/auth.md` | Setting up authentication for REST API or GraphQL calls. Token file format, path discovery, security, instance config, common auth errors. |
| `references/rest-api-fallback.md` | `acli` failed to update a custom field (Team, Size, Story Points, Release Note Type). Curl examples, response handling, OpenAPI spec discovery. |
| `references/graphql-queries.md` | Complex read queries needing multiple fields, relationships, or custom field data in one call. Schema introspection, JQL search via GraphQL, field type fragments. |

## Common Gotchas

1. **`acli auth status` lies.** It checks OAuth, not API token auth. Always returns "unauthorized" with token auth even when Jira works fine. Use `acli jira project list --recent 1` as a smoke test instead.
2. **`view` uses positional arg, everything else uses `--key`.** `acli jira workitem view RHIDP-123` but `acli jira workitem edit --key RHIDP-123 ...`.
3. **`--yes` is mandatory for mutations.** All `edit`, `transition`, `assign`, and `link create` commands prompt interactively without it. Always pass `--yes`.
4. **`--fields` is restrictive on search.** Only accepts `key`, `summary`, `status`, `assignee`, `issuetype`, `priority`, `description`, `labels`. For components, sprint, fixVersions, and all custom fields — use `--json` or `scripts/parse_issues.py --enrich`.
5. **Team field is NOT JQL-filterable.** `customfield_10001` cannot be used in JQL WHERE clauses. Fetch all issues, filter by `customfield_10001.name` in post-processing.
6. **ADF vs plain text.** Reading descriptions via `--json` returns Atlassian Document Format (nested JSON). Creating/editing with `--description` accepts plain text. Don't try to round-trip ADF through `--description`.
7. **Acceptance Criteria field is almost always null.** Scan the description for "Requirements", "Acceptance Criteria", or bullet-style criteria instead of checking `customfield_10718`.
8. **`--enrich` is MANDATORY for custom fields.** Both `acli search --json` and `acli view KEY --json` (without `--fields "*all"`) return only basic fields (assignee, issuetype, priority, status, summary). Story points, team, sprint, and size will appear as empty/null — looking like the data isn't set when it actually is. Always use `scripts/parse_issues.py --enrich` to get custom field data. Skipping `--enrich` is the #1 cause of false "missing data" reports.
9. **Custom fields may fail to update via `acli`.** `acli jira workitem edit` can silently fail or error when setting custom fields (Team, Size, Story Points). When an `acli edit` for a custom field fails, fall back to the Jira REST API. Find the token file at `.jira-token` next to the `acli` executable (discover the path with `readlink -f "$(which acli)"` or `where acli`). Read `references/rest-api-fallback.md` for curl examples and payload formats. Never read the token file into context.
10. **`acli sprint list-workitems --json` wraps results in `{"issues": [...]}`.**  The output is NOT a flat array — it's an object with an `issues` key. Extract the array before piping to `parse_issues.py`. See `references/acli-commands.md` for the workaround command.
11. **GraphQL search is beta.** `issueSearchStable` requires `X-ExperimentalApi: JiraIssueSearch` header. Load `references/graphql-queries.md` before attempting GraphQL queries.
12. **`.jira-token` format is `email:token`, not bare token.** A file containing only the API token without the email prefix will cause 401 errors on REST/GraphQL calls. The `setup.py` script validates the format.

## Error Handling

| Error | Action |
|-------|--------|
| `acli` not on PATH | Run `scripts/setup.py`. Install from Atlassian if missing. See [Getting Started](https://developer.atlassian.com/cloud/acli/guides/how-to-get-started/). |
| "unauthorized" from `auth status` | Ignore. Check `jira_config.yaml` exists. Run smoke test. |
| "required flag(s) not set" | Command syntax wrong. Run `acli jira <subcommand> --help`. |
| "field X is not allowed" | Use `--json` instead of `--fields` for that field. |
| "the value X does not exist for the field 'project'" | Project key is wrong or project is archived (e.g., RHDHPAI). |
| Rate limiting (429) | Wait 5 seconds, retry once. |
| Interactive prompt hangs | Missing `--yes` flag on a mutating command. |
| Custom field update fails via `acli` | Fall back to Jira REST API using `.jira-token` file. See Gotcha #9. |

## Common Workflows

### Creating an issue
1. Load `references/templates.md` for the body template
2. Load `references/workflows.md` for required fields at New status
3. Run `acli jira workitem create` (see `references/acli-commands.md` if unsure of syntax)

### Searching with custom fields (team, story points, sprint)
1. Build JQL using patterns from `references/jql-patterns.md`
2. Pipe results through `scripts/parse_issues.py --enrich` for full field data
3. Use `-f team="X"` to filter by team (not possible in JQL)

### Transitioning an issue
1. Load `references/workflows.md` for exit criteria at the target status
2. Verify required fields are set before transitioning
3. Run `acli jira workitem transition --key KEY --status "X" --yes`

### Complex queries (many fields, relationships)
1. Load `references/graphql-queries.md`
2. Use `issueByKey` for single issues or `issueSearchStable` (beta) for JQL search
3. Fall back to `acli` + `parse_issues.py --enrich` if GraphQL returns errors

### Discovering unknown fields or endpoints
1. For REST: load `references/rest-api-fallback.md` — use the OpenAPI spec or `/rest/api/3/field` endpoint
2. For GraphQL: load `references/graphql-queries.md` — use `__type` introspection queries
3. Do not guess field IDs or types — always verify against the live schema

## When NOT to Use

- **Non-RHDH Jira projects** — this skill's field mappings, workflows, and JQL patterns are specific to RHIDP/RHDHPLAN/RHDHBUGS/RHDHSUPP
- **Jira REST API directly** — use `acli` first. REST API is a fallback for custom field updates and schema discovery when `acli` cannot handle the operation (see Gotcha #9)
- **GraphQL for simple lookups** — use `acli` for single-issue views and simple searches. GraphQL is for complex queries needing relationships or many custom fields in one call, and for schema introspection
