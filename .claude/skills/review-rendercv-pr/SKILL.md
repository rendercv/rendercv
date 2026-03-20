---
name: review-rendercv-pr
description: Review a GitHub pull request against RenderCV's codebase standards, architecture, and test requirements, then post a detailed review.
---

# Review a RenderCV Pull Request

Review a GitHub PR for the `rendercv` repository. Analyze code quality, correctness, test coverage, and adherence to project conventions, then post a review.

## Step 1: Identify the PR

If a PR number or URL is provided, use it. Otherwise, list open PRs:

```bash
gh pr list --repo rendercv/rendercv --state open --json number,title,author,headRefName --limit 20
```

Read the PR details:

```bash
gh pr view <number> --repo rendercv/rendercv
```

## Step 2: Understand RenderCV

Before reviewing, build a deep understanding of the project:

- @.claude/skills/rendercv-development-context/SKILL.md
- @.claude/skills/rendercv-testing-context/SKILL.md

Read the referenced files, focusing on modules relevant to the PR.

## Step 3: Analyze the PR diff

Get the full diff and list of changed files:

```bash
gh pr diff <number> --repo rendercv/rendercv
```

```bash
gh pr view <number> --repo rendercv/rendercv --json files --jq '.files[].path'
```

Read the linked issue (if any) to understand the motivation:

```bash
gh pr view <number> --repo rendercv/rendercv --json body --jq '.body'
```

## Step 4: Read the full context of changed files

For every file touched by the PR, read the **full file on the PR branch** (not just the diff) to understand context:

```bash
gh pr diff <number> --repo rendercv/rendercv --patch
```

Also read the corresponding source and test files in the main branch to understand what existed before.

## Step 5: Evaluate against RenderCV standards

Check each of these categories systematically:

Evaluate the PR against @.claude/skills/rendercv-development-context/SKILL.md and @.claude/skills/rendercv-testing-context/SKILL.md. Also check for correctness (edge cases, regressions) and security (no injection, path traversal, or hardcoded secrets).

## Step 6: Check CI status

```bash
gh pr checks <number> --repo rendercv/rendercv
```

Note any failing checks — these must be resolved before merging.

## Step 7: Post the review

Compose a structured review and post it using `gh`:

```bash
gh pr review <number> --repo rendercv/rendercv \
  --body "$(cat <<'EOF'
## Review Summary

<1-2 sentence overview of the PR and its quality>

## Correctness
<findings>

## Code Conventions
<findings>

## Architecture
<findings>

## Testing
<findings>

## Other Notes
<any additional observations>
EOF
)" \
  --<event>
```

Where `<event>` is one of:

- `--approve` — Everything looks good, meets all standards.
- `--request-changes` — Issues that must be fixed before merging.
- `--comment` — Observations that don't block merging but are worth noting.

### Inline comments

For specific line-level feedback, add inline review comments:

```bash
gh api repos/rendercv/rendercv/pulls/<number>/comments \
  --method POST \
  -f body="<comment>" \
  -f commit_id="$(gh pr view <number> --repo rendercv/rendercv --json headRefOid --jq '.headRefOid')" \
  -f path="<file_path>" \
  -f side="RIGHT" \
  -F line=<line_number>
```

## Step 8: Report results

Tell the user:
1. Overall assessment (approve / request changes / comment)
2. Key findings in each category
3. Any blocking issues that must be fixed
4. Link to the posted review
