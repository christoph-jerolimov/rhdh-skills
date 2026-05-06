# Jira GraphQL API

Use the Atlassian GraphQL API for complex queries where you need multiple fields, relationships, or custom field data in a single call. For complex read queries and schema discovery via GraphQL. For REST API writes and OpenAPI schema discovery, see `references/rest-api-fallback.md`.

**Do not read the `.jira-token` file into context.** Pass it to `curl -u` via shell substitution (see Authentication below).

## Endpoint and Authentication

See `references/auth.md` for token file setup, security, and instance config (`AUTH`, `CLOUD_ID`, `JIRA_BASE`).

```bash
# Set AUTH and CLOUD_ID per references/auth.md, then:
GRAPHQL_URL="$JIRA_BASE/gateway/api/graphql"
```

## Schema Discovery

GraphQL APIs are self-describing via introspection. There is no separate spec file to download (unlike REST's OpenAPI spec). Instead, query the schema directly.

Use `__type` introspection queries to discover fields and types dynamically. Do this when encountering unknown types or before constructing a new query pattern.

#### List all Jira query entry points

```bash
curl -s -u "$AUTH" -X POST -H 'Content-Type: application/json' \
  -d '{"query": "query IntrospectJira { __type(name: \"JiraQuery\") { fields { name description type { name kind } } } }"}' \
  "$GRAPHQL_URL"
```

#### Inspect a specific type

```bash
curl -s -u "$AUTH" -X POST -H 'Content-Type: application/json' \
  -d '{"query": "query IntrospectType { __type(name: \"JiraIssue\") { fields { name type { name kind ofType { name } } } } }"}' \
  "$GRAPHQL_URL"
```

Replace `JiraIssue` with any type name from the schema (e.g., `JiraSprintField`, `JiraTeamViewField`, `User`).

#### Full schema introspection (large output)

```bash
curl -s -u "$AUTH" -X POST -H 'Content-Type: application/json' \
  -d '{"query": "query FullSchema { __schema { types { name kind fields { name type { name kind ofType { name } } } } } }"}' \
  "$GRAPHQL_URL" -o graphql-schema.json
```

The output is large (~1MB+). Do not load into context. Query it programmatically:

```bash
python -c "
import json
schema = json.load(open('graphql-schema.json'))
for t in schema['data']['__schema']['types']:
    if t['name'].startswith('Jira') and t.get('fields'):
        print(f\"{t['name']:40} {len(t['fields'])} fields\")
"
```

### Key types discovered

| Type | Fields | Notes |
|------|--------|-------|
| `JiraIssue` | `key`, `summary`, `status`, `issueType`, `priority`, `assignee`, `parentIssue`, `storyPoints`, `labels`, `fixVersions`, `fields` (edges) | `storyPoints` is a first-class Float scalar |
| `User` | `name`, `accountId`, `picture` | No `emailAddress` or `displayName` — more limited than REST |
| `JiraSprintField` | `selectedSprintsConnection`, `sprints` | Access sprint data via connection edges |
| `JiraTeamViewField` | Shows as `__typename` in field edges | Value extraction is limited — may need `@optIn` |
| `JiraNumberField` | `number` | Used for Story Points and other numeric custom fields |
| `JiraSingleSelectField` | `fieldOption { value }` | Used for Size, Ready, Blocked, Release Note Type |

## Query Patterns

### Fetch a single issue with all custom fields

```bash
curl -s -u "$AUTH" -X POST -H 'Content-Type: application/json' \
  -d '{
    "query": "query GetIssue { jira { issueByKey(key: \"RHIDP-1234\", cloudId: \"'"$CLOUD_ID"'\") { key summary status { name } issueType { name } priority { name } assignee { name } storyPoints parentIssue { key summary } fields { edges { node { __typename name ... on JiraNumberField { number } ... on JiraSingleSelectField { fieldOption { value } } ... on JiraSprintField { selectedSprintsConnection { edges { node { name state } } } } ... on JiraLabelsField { labels { edges { node { name } } } } } } } } } }"
  }' \
  "$GRAPHQL_URL"
```

This single call returns what would take `acli view` + `--enrich` + `parse_issues.py` in the acli workflow.

### Search issues via JQL (beta)

**Requires experimental header.** This endpoint can change without notice.

```bash
curl -s -u "$AUTH" -X POST \
  -H 'Content-Type: application/json' \
  -H 'X-ExperimentalApi: JiraIssueSearch' \
  -d '{
    "query": "query SearchIssues { jira { issueSearchStable(cloudId: \"'"$CLOUD_ID"'\", issueSearchInput: {jql: \"project = RHIDP AND status = \\\"In Progress\\\" ORDER BY created DESC\"}, first: 10) { totalCount pageInfo { endCursor hasNextPage } edges { node { key summary status { name } issueType { name } priority { name } assignee { name } storyPoints parentIssue { key summary } fields { edges { node { __typename name ... on JiraNumberField { number } ... on JiraSingleSelectField { fieldOption { value } } ... on JiraSprintField { selectedSprintsConnection { edges { node { name state } } } } } } } } } } } }"
  }' \
  "$GRAPHQL_URL"
```

- `first: N` controls page size (on the connection, not in `issueSearchInput`)
- `totalCount` returns the total number of matching issues (useful to know if results are truncated)
- JQL syntax is the same as REST/acli
- Returns all custom fields in one call — no `--enrich` needed

### Paginating search results

Use `pageInfo.endCursor` to fetch the next page:

```bash
# First page
# ... returns pageInfo: { endCursor: "abc123", hasNextPage: true }

# Next page — add after: "abc123"
curl -s -u "$AUTH" -X POST \
  -H 'Content-Type: application/json' \
  -H 'X-ExperimentalApi: JiraIssueSearch' \
  -d '{
    "query": "query SearchPage2 { jira { issueSearchStable(cloudId: \"'"$CLOUD_ID"'\", issueSearchInput: {jql: \"project = RHIDP AND status = \\\"In Progress\\\"\"}, first: 50, after: \"abc123\") { totalCount pageInfo { endCursor hasNextPage } edges { node { key summary } } } } }"
  }' \
  "$GRAPHQL_URL"
```

Loop until `hasNextPage` is `false`.

## Field Type Reference

Custom fields appear in `fields { edges { node { ... } } }` with typed fragments:

| `__typename` | Fragment | Returns |
|-------------|----------|---------|
| `JiraNumberField` | `... on JiraNumberField { number }` | Story Points, DEV/QE/DOC Story Points |
| `JiraSingleSelectField` | `... on JiraSingleSelectField { fieldOption { value } }` | Size (XS/S/M/L/XL), Ready, Blocked, Release Note Type |
| `JiraSprintField` | `... on JiraSprintField { selectedSprintsConnection { edges { node { name state } } } }` | Sprint name and state (active/closed/future) |
| `JiraLabelsField` | `... on JiraLabelsField { labels { edges { node { name } } } }` | All labels |
| `JiraTeamViewField` | _(no value sub-fields currently extractable)_ | Team — visible as `__typename` but value needs REST fallback |
| `JiraComponentsField` | _(introspect for sub-fields)_ | Components |
| `JiraDatePickerField` | _(introspect for sub-fields)_ | Start date, Target start/end |
| `JiraRichTextField` | _(introspect for sub-fields)_ | Description, Release Note Text, Acceptance Criteria |
| `JiraParentIssueField` | _(introspect for sub-fields)_ | Parent Link (legacy) — prefer `parentIssue` on `JiraIssue` |

When you encounter an unknown `__typename`, introspect it:

```bash
curl -s -u "$AUTH" -X POST -H 'Content-Type: application/json' \
  -d '{"query": "query Introspect { __type(name: \"JiraTeamViewField\") { fields { name type { name kind ofType { name } } } } }"}' \
  "$GRAPHQL_URL"
```

## Mutations (Experimental)

GraphQL mutations for Jira issue updates exist but are experimental. They require `@optIn` directives and may break without notice. **Use REST API `PUT /rest/api/3/issue/{key}` for writes** — it is stable and well-documented.

If you discover stable mutations in the future via introspection, verify they do not require experimental headers before relying on them.

## Caveats

1. **`issueSearchStable` is beta.** Requires `X-ExperimentalApi: JiraIssueSearch` header. May break without notice. If you get a `BetaHeaderOptInException` error, add this header.
2. **Team field values are not directly extractable.** `JiraTeamViewField` appears in the schema but value sub-fields are limited. Use REST API to get team data.
3. **`cloudId` is required on every query.** Use `2b9e35e3-6bd3-4cec-b838-f4249ee02432` for redhat.atlassian.net. Discover it via `/_edge/tenant_info` (see Authentication section).
4. **Rate limiting is cost-based.** 10,000 points per user per minute. HTTP 429 with `RETRY-AFTER` header when exceeded. Do not retry on 5xx.
5. **Operation names are mandatory.** Every query must have a name (e.g., `query GetIssue { ... }`). Unnamed queries will be rejected in the future.
6. **No spec file to download.** Unlike REST (which has an OpenAPI spec), GraphQL schema is discovered via introspection queries only. Use `__type` or the full `__schema` query. See Schema Discovery section.

## When to use GraphQL vs acli

| Scenario | Use |
|----------|-----|
| Quick single-issue lookup | `acli` — faster, simpler |
| Bulk search with custom fields | GraphQL `issueSearchStable` — one call vs `acli` + `--enrich` per issue |
| Need parent/child relationships | GraphQL — `parentIssue { key summary }` inline |
| Update a field | REST API — `PUT /rest/api/3/issue/{key}` (stable) |
| Team field value | REST API — GraphQL can't extract it reliably |
| Sprint data | Either — GraphQL returns it inline, acli needs `--enrich` |
| Discover available fields/types | GraphQL introspection — `__type` queries |
| Discover REST endpoints/payloads | REST OpenAPI spec — see `references/rest-api-fallback.md` |
