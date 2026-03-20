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

Before reviewing, build a deep understanding of the project by reading these files **in order**:

### 2a: Project metadata and dependencies

- @pyproject.toml

### 2b: Architecture and design

- @docs/developer_guide/understanding_rendercv.md

### 2c: Code guidelines

- @docs/developer_guide/code_guidelines/source_code.md

### 2d: Testing guidelines

- @docs/developer_guide/code_guidelines/tests.md
- @docs/developer_guide/testing.md

### 2e: Source structure

Explore the three top-level packages to understand the module layout:

- @src/rendercv/schema/
- @src/rendercv/renderer/
- @src/rendercv/cli/

For each, read the directory tree and skim key files relevant to the PR.

### 2f: Test structure

- @tests/

The test structure mirrors `src/rendercv/`. Read the test files in the area related to the PR.

### 2g: Available commands

- @justfile

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

### 5a: Correctness

- Does the change solve the stated problem or implement the requested feature?
- Are there edge cases not handled?
- Could the change introduce regressions?
- Is the logic sound?

### 5b: Code conventions

- **No private API syntax**: No underscore-prefixed names (`_Foo`, `_bar`). All names must be public.
- **Strict typing**: Every function, variable, and class attribute must have type annotations. Use Python 3.12+ syntax (`type` statements, `X | Y` unions, `X | None`).
- **Docstrings**: Google-style with Why/Args/Returns/Raises sections for new functions/classes.
- **No unnecessary changes**: Only code directly related to the issue should be touched. No drive-by refactors, no added comments to existing code, no unrelated "improvements."

### 5c: Architecture

- Does the change fit RenderCV's pipeline (`YAML → pydantic → jinja2 → Typst → PDF`)?
- Is code placed in the correct module? (`schema/` for models, `renderer/` for output, `cli/` for commands)
- Is the solution the simplest correct approach? No over-engineering, no duct tape.
- Is there code duplication that should be consolidated?

### 5d: Testing

- Are new code paths tested?
- Do tests follow the mirror structure (`src/rendercv/renderer/foo.py` → `tests/renderer/test_foo.py`)?
- Are tests named by expected behavior, not by input?
- Is `@pytest.mark.parametrize` used for variations instead of duplicate tests?
- Are existing fixtures from `conftest.py` files reused where appropriate?
- If output changed, were reference files updated with `just update-testdata`?

### 5e: Security and robustness

- No command injection, path traversal, or unsafe deserialization.
- User inputs validated at system boundaries.
- No hardcoded secrets or credentials.

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
