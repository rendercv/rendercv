"""Generate the ATS compatibility report from test results.

Renders ats_compatibility.j2.md with Jinja2 and writes the output to
docs/ats_compatibility.md.
"""

from pathlib import Path

import jinja2
from common import (
    ANALYSIS_DIR,
    RENDERED_DIR,
    RESULTS_DIR,
    THEMES,
    load_json,
)

SCRIPT_DIR: Path = Path(__file__).parent
REPO_ROOT: Path = SCRIPT_DIR.parent.parent
REPORT_OUTPUT: Path = REPO_ROOT / "docs" / "ats_compatibility.md"

# Fields to show in the commercial parser table, with display names
REPORT_FIELDS: list[tuple[str, str]] = [
    ("contact_name", "Name"),
    ("contact_email", "Email"),
    ("contact_phone", "Phone"),
    ("contact_location", "Location"),
    ("work_company", "Company name"),
    ("work_position", "Job title"),
    ("work_start_date", "Start date"),
    ("work_end_date", "End date"),
    ("edu_institution", "Institution"),
]

PARSER_DISPLAY_NAMES: dict[str, str] = {
    "edenai_affinda": "affinda",
    "edenai_extracta": "extracta",
    "edenai_klippa": "klippa",
}


def f1_to_checkmark(f1: float) -> str:
    """Convert an F1 score to a human-readable result."""
    if f1 >= 0.90:
        return "Correct"
    if f1 >= 0.50:
        return "Partial"
    return "Not extracted"


def build_context() -> dict:
    """Load result files and build the Jinja2 template context."""
    eval_results = load_json(ANALYSIS_DIR / "evaluation_results.json")
    struct_summary = load_json(RESULTS_DIR / "structural" / "structural_summary.json")
    extraction_summary = load_json(
        RESULTS_DIR / "opensource" / "extraction_summary.json"
    )

    has_commercial = bool(eval_results.get("evaluations"))

    # Build per-parser per-field scores
    parser_scores: dict[str, dict[str, float]] = {}
    for evaluation in eval_results.get("evaluations", []):
        parser_name = evaluation["parser"]
        parser_scores[parser_name] = evaluation["per_field"]

    # Build conformance field rows with per-parser results
    conformance_fields: list[dict] = []
    if has_commercial:
        for key, name in REPORT_FIELDS:
            row: dict = {"name": name}
            for parser_name, display_name in PARSER_DISPLAY_NAMES.items():
                f1 = parser_scores.get(parser_name, {}).get(key, 0)
                row[display_name] = f1_to_checkmark(f1)
            conformance_fields.append(row)

    # Build extractor rows
    extractors: list[dict] = [
        {"name": name, **stats}
        for name, stats in extraction_summary.get("extractors", {}).items()
    ]

    total_pdfs = len(list(RENDERED_DIR.rglob("*.pdf")))
    num_themes = len(THEMES)

    return {
        "total_pdfs": total_pdfs,
        "num_themes": num_themes,
        "num_cases": total_pdfs // num_themes if num_themes else total_pdfs,
        "struct_passed": struct_summary.get("passed", 0),
        "struct_total": struct_summary.get("total", 0),
        "struct_rate": struct_summary.get("pass_rate", "N/A"),
        "extractors": extractors,
        "has_commercial": has_commercial,
        "conformance_fields": conformance_fields,
    }


def main() -> None:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(SCRIPT_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    template = env.get_template("ats_compatibility.j2.md")

    context = build_context()
    report = template.render(context)

    REPORT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUTPUT.write_text(report, encoding="utf-8")
    print(f"Report written to {REPORT_OUTPUT}")  # noqa: T201


if __name__ == "__main__":
    main()
