# Reference: rhdh-operator PR Container Images

<image_naming>

## Image Naming Convention

The CI workflow `.github/workflows/pr-container-build.yaml` builds three images per PR:

| Image | Registry | Purpose |
|-------|----------|---------|
| Operator | `quay.io/rhdh-community/operator` | The operator binary |
| Bundle | `quay.io/rhdh-community/operator-bundle` | OLM bundle metadata |
| Catalog | `quay.io/rhdh-community/operator-catalog` | OLM catalog index |

**Tag format:** `VERSION-pr-PR_NUMBER-SHORT_SHA`

Example for PR #2756 at commit `6926c0b` with Makefile `VERSION=0.10.0`:

```
quay.io/rhdh-community/operator:0.10.0-pr-2756-6926c0b
quay.io/rhdh-community/operator-bundle:0.10.0-pr-2756-6926c0b
quay.io/rhdh-community/operator-catalog:0.10.0-pr-2756-6926c0b
```

A short tag (without commit SHA) is also pushed: `0.10.0-pr-2756`

</image_naming>

<expiry>

## Image Expiry

PR images are labeled with `quay.expires-after=14d` and automatically deleted from Quay after 14 days. If images have expired, the PR author needs to push a new commit to trigger a fresh build.

</expiry>

<extracting_from_pr>

## Extracting Image URLs from PR Comments

The CI workflow posts a comment on the PR with built image URLs. Extract them with:

```bash
REPO="redhat-developer/rhdh-operator"
PR_NUMBER=<number>

gh pr view $PR_NUMBER --repo $REPO --json comments \
  --jq '.comments[] | select(.body | test("quay.io/rhdh-community/operator:")) | .body'
```

If no comment is found, check whether the CI workflow is still running:

```bash
BRANCH=$(gh pr view $PR_NUMBER --repo $REPO --json headRefName --jq '.headRefName')
gh run list --repo $REPO --branch $BRANCH --workflow pr-container-build.yaml --limit 1 \
  --json status,conclusion
```

- `status: in_progress` — workflow still running, wait for it
- `conclusion: failure` — build failed, check workflow logs
- No runs found — CI may not have been triggered (draft PR, docs-only change, or external contributor awaiting approval)

</extracting_from_pr>

<validation>

## Validating Images Exist

Use skopeo or podman to check if an image exists in the registry:

```bash
skopeo inspect docker://quay.io/rhdh-community/operator:TAG --raw 2>/dev/null \
  && echo "Image exists" || echo "Image not found or expired"
```

If skopeo is not available, use podman:

```bash
podman pull --quiet quay.io/rhdh-community/operator:TAG 2>/dev/null \
  && echo "Image exists" || echo "Image not found or expired"
```

</validation>
