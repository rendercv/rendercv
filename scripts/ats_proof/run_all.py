"""Run the ATS compatibility test pipeline.

Usage:
    uv run python run_all.py              # Local analysis (free, no API keys)
    uv run python run_all.py --commercial # Also run commercial parsers (needs API keys)
    uv run python run_all.py --full       # All + evaluate + report
"""

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR: Path = Path(__file__).parent

STEPS_LOCAL: list[tuple[str, str]] = [
    ("render_pdfs.py", "Render PDFs across all themes"),
    ("analyze_pdfs.py", "Run structural + extraction analysis"),
]

STEPS_COMMERCIAL: list[tuple[str, str]] = [
    ("submit_commercial.py", "Submit to commercial parsers"),
]

STEPS_REPORT: list[tuple[str, str]] = [
    ("evaluate.py", "Evaluate results against ground truth"),
    ("generate_report.py", "Generate report"),
]


def run_step(script: str, description: str) -> None:
    """Run a script, exit on failure."""
    print(f"\n{'=' * 60}")  # noqa: T201
    print(f"  {description}")  # noqa: T201
    print(f"{'=' * 60}")  # noqa: T201
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / script)],
        check=False,
    )
    if result.returncode != 0:
        print(f"\nFAILED: {description}")  # noqa: T201
        sys.exit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description="ATS compatibility test pipeline")
    parser.add_argument(
        "--commercial", action="store_true", help="Include commercial parsers"
    )
    parser.add_argument(
        "--full", action="store_true", help="Full pipeline including report"
    )
    args = parser.parse_args()

    for script, desc in STEPS_LOCAL:
        run_step(script, desc)

    if args.commercial or args.full:
        for script, desc in STEPS_COMMERCIAL:
            run_step(script, desc)

    if args.full:
        for script, desc in STEPS_REPORT:
            run_step(script, desc)

    print("\nDone.")  # noqa: T201


if __name__ == "__main__":
    main()
