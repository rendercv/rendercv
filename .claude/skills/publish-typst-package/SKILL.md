---
name: publish-typst-package
description: Create a PR to publish a new version of the rendercv-typst package to the Typst Universe (typst/packages repository). Validates package integrity, forks/clones the repo, copies files, and opens a PR.
disable-model-invocation: true
---

# Publish rendercv-typst to Typst Universe

Create a pull request to `typst/packages` to publish the current version of `rendercv-typst/`.

The clone location for the typst/packages fork is `$HOME/.cache/rendercv/typst-packages`.

## Step 1: Read package metadata

Read `rendercv-typst/typst.toml` to get the version and all metadata fields.

## Step 2: Validate package integrity

Run ALL checks below. Collect ALL failures and report them together. Do NOT proceed to Step 3 if any check fails.

### 2a: Required files

Verify these exist in `rendercv-typst/`:
- `lib.typ`
- `typst.toml`
- `README.md`
- `LICENSE`
- `thumbnail.png`
- `template/main.typ`

### 2b: Manifest completeness

Parse `typst.toml` and verify it has:
- Required: `name`, `version`, `entrypoint`, `authors`, `license`, `description`
- Template section: `[template]` with `path`, `entrypoint`, `thumbnail`

### 2c: Version consistency

Check that the version string in `typst.toml` appears correctly in:
- `README.md` import statements (`@preview/rendercv:X.Y.Z`)
- `template/main.typ` import statement (`@preview/rendercv:X.Y.Z`)
- All example files in `rendercv-typst/examples/*.typ` (if they have import statements)

If ANY file references an old version, stop and report which files need updating.

### 2d: CHANGELOG entry

Read `rendercv-typst/CHANGELOG.md` and verify there is an entry for the version being published.

### 2e: All themes have example files

This is critical. Extract all theme names shown in the README by finding image references that match the pattern `examples/<theme-name>.png` in the image URLs. Then verify that EVERY theme has a corresponding `<theme-name>.typ` file in `rendercv-typst/examples/`.

For example, if the README shows images for classic, engineeringresumes, sb2nov, moderncv, engineeringclassic, and harvard, then ALL of these must exist as `.typ` files in `rendercv-typst/examples/`.

If any example file is missing, STOP and tell the user exactly which files are missing.

### 2f: No stale or broken links

Check that the `README.md` does not reference nonexistent files within the package (e.g., broken relative links).

### 2g: Import style in template

Verify `template/main.typ` uses the absolute package import (`@preview/rendercv:{version}`) and NOT a relative import like `../lib.typ`. The Typst packages repository requires absolute imports.

## Step 3: Handle previous work

1. Check for existing open PRs for rendercv in `typst/packages`:
   ```
   gh pr list --repo typst/packages --author @me --search "rendercv" --state all
   ```

2. If an existing PR is **open**, ask the user what to do:
   - Update the existing PR?
   - Close it and create a new one?
   - Abort?

3. If the clone directory `$HOME/.cache/rendercv/typst-packages` already exists:
   - If there are old branches for previous versions that have been merged/closed, delete them.
   - Reset to upstream/main before proceeding.

## Step 4: Set up fork and clone

### If clone does NOT exist:

```bash
mkdir -p $HOME/.cache/rendercv
# Fork if not already forked (idempotent)
gh repo fork typst/packages --clone=false
# Clone with sparse checkout
gh repo clone $(gh api user --jq .login)/packages $HOME/.cache/rendercv/typst-packages -- --filter=blob:none --sparse
cd $HOME/.cache/rendercv/typst-packages
git sparse-checkout set packages/preview/rendercv
git remote add upstream https://github.com/typst/packages.git 2>/dev/null || true
git fetch upstream main
```

### If clone ALREADY exists:

```bash
cd $HOME/.cache/rendercv/typst-packages
git fetch upstream main
git checkout main
git reset --hard upstream/main
```

## Step 5: Create the package version directory

1. Read the version from `typst.toml` (e.g., `0.3.0`).
2. Create a new branch: `git checkout -b rendercv-{version}`
3. Create the target directory: `packages/preview/rendercv/{version}/`
4. Copy files from the rendercv-typst source directory into the target:

**Files to copy:**
- `lib.typ`
- `typst.toml`
- `README.md`
- `LICENSE`
- `thumbnail.png`
- `template/` (entire directory)
- `examples/` (entire directory, but exclude any `.pdf` files)

**Do NOT copy:**
- `CHANGELOG.md`
- `.git/` or `.gitignore`
- Any `.pdf` files

5. Verify no PDF files ended up in the target directory.

## Step 6: Determine previous version

Look at existing directories in `packages/preview/rendercv/` to find the most recent previous version. This is needed for the PR description. If no previous version exists (first submission), note that this is a new package.

## Step 7: Build PR description

Read `rendercv-typst/CHANGELOG.md` and extract the changes for the current version.

**PR title:** `rendercv:{version}`

**PR body for updates:**
```
I am submitting
  - [ ] a new package
  - [x] an update for a package

Description: {Brief description of the package}. {Summary of what changed in this version}.

### Changes from {previous_version}

{Bullet list of changes extracted from CHANGELOG.md}
```

**PR body for new packages** (if no previous version exists, include the full checklist):
```
I am submitting
  - [x] a new package
  - [ ] an update for a package

Description: {Description from typst.toml}

I have read and followed the submission guidelines and, in particular, I
- [x] selected a name that isn't the most obvious or canonical name for what the package does
- [x] added a `typst.toml` file with all required keys
- [x] added a `README.md` with documentation for my package
- [x] have chosen a license and added a `LICENSE` file or linked one in my `README.md`
- [x] tested my package locally on my system and it worked
- [x] `exclude`d PDFs or README images, if any, but not the LICENSE
- [x] ensured that my package is licensed such that users can use and distribute the contents of its template directory without restriction, after modifying them through normal use.
```

## Step 8: Commit, push, and create PR

```bash
cd $HOME/.cache/rendercv/typst-packages
git add packages/preview/rendercv/{version}/
git commit -m "rendercv:{version}"
git push -u origin rendercv-{version}
```

Create the PR:
```bash
gh pr create \
  --repo typst/packages \
  --base main \
  --title "rendercv:{version}" \
  --body "..." # Use the body from Step 7
```

## Step 9: Report results

Tell the user:
1. The PR URL (clickable)
2. The clone location (`$HOME/.cache/rendercv/typst-packages`)
3. The branch name (`rendercv-{version}`)
4. Any warnings noticed during validation (even if they didn't block the PR)
