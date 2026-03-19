"""Analyze rendered PDFs: structural checks and text extraction.

Structural: pdftotext/pdfinfo via Poppler.
Extraction: pdftotext (Poppler) and PyMuPDF — two independent tools that
cover the standard extraction path used by most ATS platforms.
"""

import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import fitz  # PyMuPDF
from common import (
    RENDERED_DIR,
    RESULTS_DIR,
    check_garbled,
    compute_accuracy,
    find_rendered_pdfs,
    find_yaml_for_pdf,
    get_expected_strings,
    normalize_quotes,
    write_json,
)
from ruamel.yaml import YAML

# ---------------------------------------------------------------------------
# Extractors
# ---------------------------------------------------------------------------


def extract_pdftotext(pdf_path: Path) -> str:
    """Extract text using Poppler's pdftotext."""
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return result.stdout


def extract_pymupdf(pdf_path: Path) -> str:
    """Extract text using PyMuPDF."""
    doc = fitz.open(str(pdf_path))
    text = "".join(page.get_text() for page in doc)
    doc.close()
    return text


EXTRACTORS: dict[str, Callable[[Path], str]] = {
    "pdftotext": extract_pdftotext,
    "pymupdf": extract_pymupdf,
}


# ---------------------------------------------------------------------------
# Structural checks
# ---------------------------------------------------------------------------


def check_poppler_installed() -> bool:
    """Check if pdftotext is available."""
    try:
        subprocess.run(
            ["pdftotext", "-v"], capture_output=True, timeout=10, check=False
        )
        return True
    except FileNotFoundError:
        return False


def check_reading_order(extracted: str, name: str) -> dict:
    """Check that the CV name appears near the top of extracted text."""
    lines = [line.strip() for line in extracted.split("\n") if line.strip()]
    result: dict = {"correct": True, "issues": []}

    if not name:
        return result

    for line in lines[:10]:
        if normalize_quotes(name) in normalize_quotes(line):
            return result

    result["correct"] = False
    result["issues"].append(f"Name not found in first 10 lines: {name}")
    return result


# ---------------------------------------------------------------------------
# Single-PDF analysis
# ---------------------------------------------------------------------------


def analyze_pdf(pdf_path: Path) -> dict:
    """Run all extractors and structural checks on a single PDF."""
    yaml_path = find_yaml_for_pdf(pdf_path)
    expected = get_expected_strings(yaml_path) if yaml_path else []

    # Get CV name for reading order check
    name = ""
    if yaml_path:
        yaml = YAML()
        with yaml_path.open(encoding="utf-8") as f:
            data = yaml.load(f)
        name = data.get("cv", {}).get("name", "")

    result: dict = {
        "pdf": str(pdf_path.relative_to(RENDERED_DIR)),
        "extractors": {},
        "structural": {
            "text_extractable": False,
            "no_garbled": True,
            "reading_order": True,
        },
    }

    for ext_name, extractor in EXTRACTORS.items():
        try:
            text = extractor(pdf_path)
            accuracy = compute_accuracy(text, expected)
            garbled = check_garbled(text)

            result["extractors"][ext_name] = {
                "success": True,
                "text_length": len(text),
                "accuracy": accuracy["accuracy"],
                "fields_found": accuracy["found"],
                "fields_total": accuracy["total"],
                "missing": accuracy["missing"],
                "garbled": garbled,
            }

            # Use pdftotext for structural checks
            if ext_name == "pdftotext":
                result["structural"]["text_extractable"] = len(text.strip()) > 0
                result["structural"]["no_garbled"] = len(garbled) == 0
                reading = check_reading_order(text, name)
                result["structural"]["reading_order"] = reading["correct"]
                result["structural"]["reading_issues"] = reading["issues"]

        except Exception as e:
            result["extractors"][ext_name] = {"success": False, "error": str(e)}

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    if not check_poppler_installed():
        print("ERROR: poppler-utils not found.")  # noqa: T201
        print("  macOS: brew install poppler")  # noqa: T201
        print("  Ubuntu: apt install poppler-utils")  # noqa: T201
        sys.exit(1)

    pdfs = find_rendered_pdfs()
    if not pdfs:
        print("No PDFs found in rendered/. Run render_pdfs.py first.")  # noqa: T201
        sys.exit(1)

    print(f"Analyzing {len(pdfs)} PDFs with {len(EXTRACTORS)} extractors...")  # noqa: T201

    all_results: list[dict] = []
    structural_pass = 0
    extractor_stats: dict[str, dict] = {
        name: {"total": 0, "accuracy_sum": 0.0, "garbled": 0} for name in EXTRACTORS
    }

    for pdf_path in pdfs:
        result = analyze_pdf(pdf_path)
        all_results.append(result)

        # Structural pass/fail
        s = result["structural"]
        passed = s["text_extractable"] and s["no_garbled"] and s["reading_order"]
        if passed:
            structural_pass += 1

        # Extractor stats
        statuses: list[str] = []
        for ext_name, ext_result in result["extractors"].items():
            if ext_result.get("success"):
                extractor_stats[ext_name]["total"] += 1
                extractor_stats[ext_name]["accuracy_sum"] += ext_result["accuracy"]
                if ext_result.get("garbled"):
                    extractor_stats[ext_name]["garbled"] += 1
                statuses.append(f"{ext_name}={ext_result['accuracy']:.0%}")
            else:
                statuses.append(f"{ext_name}=FAIL")

        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {result['pdf']} ({', '.join(statuses)})")  # noqa: T201

    # Write structural results
    structural_summary = {
        "total": len(pdfs),
        "passed": structural_pass,
        "failed": len(pdfs) - structural_pass,
        "pass_rate": f"{structural_pass / len(pdfs) * 100:.1f}%",
    }
    write_json(RESULTS_DIR / "structural" / "structural_results.json", all_results)
    write_json(
        RESULTS_DIR / "structural" / "structural_summary.json", structural_summary
    )

    # Write extraction summary
    extraction_summary: dict = {"total_pdfs": len(pdfs), "extractors": {}}
    for name, stats in extractor_stats.items():
        total = stats["total"]
        avg = stats["accuracy_sum"] / total if total > 0 else 0
        extraction_summary["extractors"][name] = {
            "pdfs_tested": total,
            "average_accuracy": f"{avg:.1%}",
            "garbled_count": stats["garbled"],
        }
    write_json(RESULTS_DIR / "opensource" / "extraction_results.json", all_results)
    write_json(
        RESULTS_DIR / "opensource" / "extraction_summary.json", extraction_summary
    )

    # Print summary
    print(  # noqa: T201
        f"\nStructural: {structural_pass}/{len(pdfs)} passed ({structural_summary['pass_rate']})"
    )
    for name, s in extraction_summary["extractors"].items():
        print(  # noqa: T201
            f"Extraction ({name}): {s['average_accuracy']} avg accuracy, {s['garbled_count']} garbled"
        )

    if structural_pass < len(pdfs):
        print(  # noqa: T201
            f"\nWARNING: {len(pdfs) - structural_pass} PDFs failed structural analysis."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
