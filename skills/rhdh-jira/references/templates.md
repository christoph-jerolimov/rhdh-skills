# Issue Templates

Jira wiki markup templates for each issue type. Use with `--description` or `--description-file` when creating issues via `acli jira workitem create`.

## Outcome Template

Project: RHDHPLAN | Type: Outcome

```
h3. *Description:*

_Provide a quick overview of the goal and key background or context._
<your text here>

h3. *Benefits/Value:*

_What are the benefits or value for our customers if we do this?_
 *  

h3. *Acceptance Criteria:*

_What must be true for this to be considered complete?_
 *  

h3. *Out of Scope:*

_If there are significant scope constraints, note them so goals and non-goals are clear._
 *  

h3. *Metrics:*

_What metrics and telemetry data influence this and either help inform this work, or could help us understand its impact?_
 *  

h3. *Dependencies:*

_Note any major team or technology dependencies outside of our direct control that we may need to plan around._
 *  
```

## Feature Template

Project: RHDHPLAN | Type: Feature

```
h1. *Feature Overview (aka. Goal Summary)*

An elevator pitch (value statement) that describes the Feature in a clear, concise way.

<your text here>

h3. *Goals (aka. expected user outcomes)*

The observable functionality that the user now has as a result of receiving this feature. Include the anticipated primary user type/persona and which existing features, if any, will be expanded.

<your text here>

h3. *Requirements (aka. Acceptance Criteria):*

A list of specific needs or objectives that a feature must deliver in order to be considered complete. If the feature spans across releases then good to have scope for each release with acceptance criteria. Be sure to include nonfunctional requirements such as security, reliability, performance, maintainability, scalability, usability, etc.

<enter general Feature acceptance here>

h3. *Out of Scope (Optional)*

High-level list of items that are out of scope.

<your text here>

h3. *Customer Considerations (Optional)*

Provide any additional customer-specific considerations that must be made when designing and delivering the Feature. Initial completion during Refinement status.

<your text here>

h3. *Documentation Considerations*

Provide information that needs to be considered and planned so that documentation will meet customer needs. If the feature extends existing functionality, provide a link to its current documentation.

<your text here>

h3. *Upstream engagement*

Review ideas/need with upstream SIGs to determine how best to interact with community
```

## Epic Template

Project: RHIDP | Type: Epic

```
h1. EPIC Goal

What are we trying to solve here?

h2. *Background/Feature Origin*

h2. *Why is this important?*

h2. *User Scenarios*

h2. *Dependencies (internal and external)*

h2. *Acceptance Criteria*

(?) Release Enablement/Demo - Provide necessary release enablement details and documents
(?) DEV - Upstream code and tests merged: <link to meaningful PR or GitHub Issue>
(?) DEV - Upstream documentation merged: <link to meaningful PR or GitHub Issue>
(?) DEV - Downstream build attached to advisory: <link to errata>
(?) QE - Test plans in Playwright: <link or reference to playwright>
(?) QE - Automated tests merged: <link or reference to automated tests>
(?) DOC - Downstream documentation merged: <link to meaningful PR>
```

## Story Template

Project: RHIDP | Type: Story

```
h1. Story

As a user of RHDH, I want to <ACTION> so that <THIS OUTCOME>

h2. *Background*

h2. *Dependencies and Blockers*
(?) QE impacted work
(?) Documentation impacted work

h2. *Acceptance Criteria*
(?) upstream documentation updates (design docs, release notes etc)
(?) Technical enablement / Demo
```

## Task Template

Project: RHIDP | Type: Task

```
h1. Task

As an engineer working on RHDH, I want to <ACTION> so that <THIS OUTCOME>

h2. *Background*

h2. *Dependencies and Blockers*
(?) QE impacted work
(?) Documentation impacted work

h2. *Acceptance Criteria*
```

## Bug Template

Project: RHDHBUGS | Type: Bug

```
h2. *Description of problem:*

h2. *Prerequisites (if any, like setup, operators/versions):*

h2. *Steps to Reproduce*
 # <steps>

h2. *Actual results:*

h2. *Expected results:*

h2. *Reproducibility (Always/Intermittent/Only Once):*

h2. *Build Details:*

h2. *Additional info (Such as Logs, Screenshots, etc):*
```

**Important for support-originated bugs:** Do not include any customer-related information in RHDHBUGS issues. RHDHBUGS is a public project. Customer details stay in RHDHSUPP.

## Feature Request Template

Project: RHDHPLAN | Type: Feature Request

```
h1. Requested Feature Overview (aka. Goal Summary)

An elevator pitch (value statement) that describes the desired Feature in a clear, concise way.

<your text here>

h3. Goals (aka. expected user outcomes)

The observable functionality that the user would have as a result of receiving this feature. Include the anticipated primary user type/persona.

<your text here>

h3. Requirements (aka. Acceptance Criteria):

A list of specific needs, objectives, or user stories that must be delivered in order to be considered complete.

<enter general Feature acceptance here>

h3. Out of Scope (Optional)

High-level list of items that are out of scope.

<your text here>

h3. Customer Considerations (Optional)

Provide any additional customer-specific considerations that must be made when designing and delivering the Feature.

<your text here>
```

## Usage Example

Save a template to a file and create the issue:

```bash
# Write template to file, fill in details
cat > epic.txt << 'EOF'
h1. EPIC Goal
Implement SSO integration for RHDH admin console.
h2. *Background/Feature Origin*
Customer requests for enterprise SSO support.
h2. *Acceptance Criteria*
(?) DEV - SSO login flow working with OIDC providers
(?) QE - E2E tests for SSO login/logout
(?) DOC - Admin guide updated with SSO configuration steps
EOF

# Create the issue
acli jira workitem create --project RHIDP --type Epic \
  --summary "SSO Integration for Admin Console" \
  --description-file epic.txt \
  --assignee "@me" \
  --label "must-have"
```
