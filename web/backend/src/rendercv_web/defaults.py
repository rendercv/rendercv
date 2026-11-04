"""Default documents seeded for a brand-new CV.

Why they are generated from the core's sample rather than written out here:
    A new CV used to open as three lines -- a name and an empty `sections`
    map -- with the other three panes empty. Nothing was broken, but it
    left the editor's whole point invisible: someone arriving at a CV
    builder saw a blank page and had to know the schema before they could
    type anything.

    The core already ships the filled-in example behind `rendercv new`, the
    same one the README screenshots show, so the editor opens on that and a
    new user edits rather than invents. Generating it keeps one source of
    truth: the sample changes when the core's schema changes, and pasted
    copies -- close to 350 lines across four documents -- would quietly
    drift out of date.

Why `design` and `locale` are uncommented:
    The generator emits those two blocks almost entirely as comments: one
    live key and roughly 130 commented-out options apiece. That is right
    for a file someone opens in an editor with no other UI, and wrong here.
    Checked against rendercv.com itself (2026-09-06), which is the product
    this one is modelled on: its Design and Locale panes show every option
    as a live, editable value. So the comment markers come off, which turns
    a list of things you could set into a list of what is currently set.

Why `settings` drops `render_command`:
    The rest of that block is about the command-line tool --
    `output_folder`, `typst_path`, `png_path`, `dont_generate_pdf`. None of
    it applies to a browser that renders server-side and offers a download
    button, so seeding it would describe a program the user is not running.
    rendercv.com omits it too, keeping only `current_date`,
    `bold_keywords` and `pdf_title`.

Why the `# yaml-language-server:` hint is dropped:
    It drives IDE autocompletion, does nothing in a browser, and pins a
    version tag that would go stale.

Why `documents.ts` is no longer kept identical to this:
    It used to be, by hand. It no longer needs to be: the frontend's copy
    is a placeholder shown for the moment before bootstrap calls
    `POST /api/cvs`, and what comes back from that call is what the user
    edits.
"""

import functools

from rendercv.schema.sample_generator import create_sample_yaml_input_file

DEFAULT_CV_NAME = "Untitled CV"

# Everything under this key configures the `rendercv` command-line tool and
# means nothing to the web editor.
CLI_ONLY_SETTINGS_KEY = "render_command"

# Fallbacks if the generator's output ever stops carrying one of these
# blocks. A pane opening empty is a poor experience; a 500 on "create CV"
# would be a broken one.
MINIMAL_CV_YAML = "cv:\n  name: John Doe\n  sections: {}\n"
MINIMAL_SETTINGS_YAML = "settings:\n  pdf_title: NAME - CV\n"


def top_level_block(document: str, key: str) -> list[str]:
    """Take one top-level block out of a full sample document.

    Why by line prefix rather than by parsing: the sample's value is partly
    in its formatting -- key order, blank lines, the comments explaining
    each entry type. Round-tripping it through a YAML loader would rebuild
    it as the dumper prefers and lose exactly the parts a beginner reads.

    Args:
        document: A full RenderCV YAML document.
        key: The top-level key to extract, without its colon.

    Returns:
        The block's lines including the key line, or an empty list if the
        document has no such top-level key.
    """
    lines = document.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.startswith(f"{key}:"))
    except StopIteration:
        return []

    end = len(lines)
    for index in range(start + 1, len(lines)):
        line = lines[index]
        # A non-empty line with no leading whitespace is the next top-level
        # key, so this block ended on the line before it.
        if line and not line[0].isspace():
            end = index
            break

    return lines[start:end]


def uncomment(lines: list[str]) -> list[str]:
    """Turn `# key: value` into `key: value`, preserving indentation.

    Only the one comment marker the generator adds is removed, and only
    from the front of a line. A `#` appearing inside a value is left alone,
    since it is part of the value rather than a marker.

    Args:
        lines: Lines of a YAML block.

    Returns:
        The same lines with a leading `# ` (or a lone `#`) taken off.
    """
    result = []
    for line in lines:
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if stripped.startswith("# "):
            result.append(" " * indent + stripped[2:])
        elif stripped == "#":
            result.append("")
        else:
            result.append(line)
    return result


def drop_subtree(lines: list[str], key: str) -> list[str]:
    """Remove a nested key and everything indented under it.

    Args:
        lines: Lines of a YAML block.
        key: The nested key to drop, without its colon.

    Returns:
        The lines with that subtree removed.
    """
    result: list[str] = []
    dropping_at: int | None = None
    for line in lines:
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if dropping_at is not None:
            # Still inside the subtree while lines stay more indented than
            # the key itself; a blank line does not end it.
            if not stripped or indent > dropping_at:
                continue
            dropping_at = None

        if stripped.startswith(f"{key}:"):
            dropping_at = indent
            continue

        result.append(line)
    return result


def as_document(lines: list[str]) -> str:
    """Join block lines into a document with exactly one trailing newline.

    Args:
        lines: The block's lines.

    Returns:
        The document text, or the empty string for an empty block.
    """
    text = "\n".join(lines).rstrip()
    return f"{text}\n" if text else ""


@functools.cache
def sample_document() -> str:
    """The core's sample CV, generated once.

    Why cached: it costs about 70 ms and cannot change within a process,
    so `POST /api/cvs` should not pay for it on every call.

    Returns:
        The full sample YAML document.
    """
    return create_sample_yaml_input_file(file_path=None)


@functools.cache
def default_cv_yaml() -> str:
    """The starter CV document, as the sample writes it.

    Returns:
        The `cv:` block, or `MINIMAL_CV_YAML` if the sample has none.
    """
    return as_document(top_level_block(sample_document(), "cv")) or MINIMAL_CV_YAML


@functools.cache
def default_design_yaml() -> str:
    """The starter design document, with every option live.

    Returns:
        The `design:` block with its comment markers removed, or the empty
        string if the sample has no such block -- which the editor reads as
        "use the theme's defaults", so the pane still works.
    """
    return as_document(uncomment(top_level_block(sample_document(), "design")))


@functools.cache
def default_locale_yaml() -> str:
    """The starter locale document, with every option live.

    Returns:
        The `locale:` block with its comment markers removed, or the empty
        string if the sample has no such block.
    """
    return as_document(uncomment(top_level_block(sample_document(), "locale")))


@functools.cache
def default_settings_yaml() -> str:
    """The starter settings document, minus the command-line options.

    Returns:
        The `settings:` block without its `render_command` subtree, or
        `MINIMAL_SETTINGS_YAML` if the sample has no such block.
    """
    block = top_level_block(sample_document(), "settings")
    kept = drop_subtree(uncomment(block), CLI_ONLY_SETTINGS_KEY)
    return as_document(kept) or MINIMAL_SETTINGS_YAML
