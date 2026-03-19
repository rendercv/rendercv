"""Render all corpus YAML files across all RenderCV themes.

For each YAML in corpus/, generates PDFs for all 5 themes using the
RenderCV Python API. Output goes to rendered/{theme}/{category}/{name}.pdf.
"""

import sys
import tempfile
from pathlib import Path

from common import RENDERED_DIR, THEMES, find_corpus_yamls

from rendercv.cli.render_command.progress_panel import ProgressPanel
from rendercv.cli.render_command.run_rendercv import run_rendercv


def render_with_theme(yaml_path: Path, theme: str, output_dir: Path) -> Path | None:
    """Render a corpus YAML with a given theme using the RenderCV API."""
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = yaml_path.stem
    pdf_path = (output_dir / f"{stem}.pdf").resolve()

    with tempfile.TemporaryDirectory() as tmp:
        run_rendercv(
            yaml_path.resolve(),
            progress=ProgressPanel(),
            pdf_path=pdf_path,
            typst_path=Path(tmp).resolve() / f"{stem}.typ",
            dont_generate_html=True,
            dont_generate_markdown=True,
            dont_generate_png=True,
            overrides={"design": {"theme": theme}},
        )

    return pdf_path if pdf_path.exists() else None


def main() -> None:
    yamls = find_corpus_yamls()
    if not yamls:
        print("No YAML files found in corpus/.")  # noqa: T201
        sys.exit(1)

    total = len(yamls) * len(THEMES)
    print(f"Rendering {len(yamls)} YAMLs x {len(THEMES)} themes = {total} PDFs...")  # noqa: T201

    success = 0
    failed = 0

    for yaml_path in yamls:
        category = yaml_path.parent.name
        for theme in THEMES:
            output_dir = RENDERED_DIR / theme / category
            pdf = render_with_theme(yaml_path, theme, output_dir)
            if pdf:
                success += 1
                print(f"  [{success}/{total}] {theme}/{category}/{yaml_path.stem}.pdf")  # noqa: T201
            else:
                failed += 1
                print(f"  FAILED: {theme}/{category}/{yaml_path.stem}")  # noqa: T201

    print(f"\nDone. {success} succeeded, {failed} failed out of {total}.")  # noqa: T201


if __name__ == "__main__":
    main()
