---
name: triage-rendercv-issue
description: Analyze a newly opened GitHub issue, comment with findings and an action plan, and offer to open a PR.
---

# Triage a RenderCV Issue

Analyze a newly opened issue on the `rendercv/rendercv` repository. Post a helpful comment that demonstrates understanding of the problem and offers next steps.

## Step 1: Read the issue

Get the full issue details including all comments:

```bash
gh issue view <number> --repo rendercv/rendercv --comments
```

Determine:

- Is this a bug report, feature request, question, or something else?
- Is there enough information to understand and reproduce the problem?
- Is this a duplicate of an existing issue?

Check for duplicates:

```bash
gh issue list --repo rendercv/rendercv --state all --search "<key terms from issue>" --json number,title,state --limit 10
```

## Step 2: Understand the relevant code

Familiarize yourself with the project architecture and the specific area the issue relates to:

- @.claude/skills/rendercv-development-context/SKILL.md

Read the architecture and source structure sections, then explore the specific source files and tests related to the issue.

## Step 3: Post a comment

Comment on the issue using `gh`:

```bash
gh issue comment <number> --repo rendercv/rendercv --body "$(cat <<'EOF'
<comment content>
EOF
)"
```

### Comment structure

1. **Understanding**: Restate the problem in your own words to confirm you understand it.
2. **Analysis**: Which files and modules are involved, what the current behavior is, and why the issue occurs (or what would need to change for a feature request).
3. **Proposed approach**: Concrete steps to fix or implement this, referencing specific files and functions.
4. **What to avoid**: Approaches that would be wrong, overly complex, or against the project's conventions.
5. **Offer**: End with: _"Reply `@claude` followed by your instructions if you'd like me to open a PR for this."_

### Guidelines

- Be concise and specific. Reference actual file paths.
- If the issue is unclear or missing information, ask clarifying questions instead of guessing.
- If it's a duplicate, out of scope, or `wontfix` material, explain why politely and suggest closing.
- If it's a question (not a bug or feature), answer it directly.
- Follow the project's conventions from the development context when discussing the approach.
- Don't promise timelines or complexity estimates.
- Don't label or assign the issue unless explicitly asked.
