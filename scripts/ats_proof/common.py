"""Shared constants and utilities for ATS compatibility testing."""

import json
import re
from pathlib import Path

from ruamel.yaml import YAML

SCRIPT_DIR: Path = Path(__file__).parent
CORPUS_DIR: Path = SCRIPT_DIR / "corpus"
RENDERED_DIR: Path = SCRIPT_DIR / "rendered"
RESULTS_DIR: Path = SCRIPT_DIR / "results"
ANALYSIS_DIR: Path = SCRIPT_DIR / "analysis"

EXPERIENCE_SECTION_NAMES: set[str] = {
    "experience",
    "work_experience",
    "work",
    "employment",
    "professional_experience",
    "volunteer_work",
    "academic_positions",
}
EDUCATION_SECTION_NAMES: set[str] = {"education"}
SKILLS_SECTION_NAMES: set[str] = {"skills", "technical_skills", "languages"}
THEMES: list[str] = [
    "classic",
    "moderncv",
    "sb2nov",
    "engineeringresumes",
    "engineeringclassic",
]

GARBLED_PATTERNS: list[str] = [
    "\ufffd",
    "\x00",
    "\u00e2\u0080\u0093",
    "\u00e2\u0080\u0099",
    "\u00e2\u0080\u009c",
    "\u00e2\u0080\u009d",
]

QUOTE_REPLACEMENTS: dict[str, str] = {
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "-",
    "\u2014": "--",
}


def normalize_quotes(text: str) -> str:
    """Normalize smart quotes and typographic characters to ASCII."""
    for old, new in QUOTE_REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


def strip_markdown(text: str) -> str:
    """Remove markdown formatting from text."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    return text.strip()


def find_corpus_yamls() -> list[Path]:
    """Find all YAML files across corpus subdirectories."""
    yamls: list[Path] = []
    for subdir in sorted(CORPUS_DIR.iterdir()):
        if subdir.is_dir():
            yamls.extend(sorted(subdir.glob("*.yaml")))
    return yamls


def find_rendered_pdfs() -> list[Path]:
    """Find all rendered PDF files."""
    return sorted(RENDERED_DIR.rglob("*.pdf"))


def find_yaml_for_pdf(pdf_path: Path) -> Path | None:
    """Find the corpus YAML file corresponding to a rendered PDF by stem."""
    stem = pdf_path.stem
    for subdir in CORPUS_DIR.iterdir():
        if subdir.is_dir():
            yaml_path = subdir / f"{stem}.yaml"
            if yaml_path.exists():
                return yaml_path
    return None


def get_expected_strings(yaml_path: Path) -> list[str]:
    """Extract expected text strings from corpus YAML for comparison.

    Returns flat list of key strings that should appear in the extracted PDF
    text. Includes contact info, section content, highlights, and dates to
    give a thorough check of text layer completeness.
    """
    yaml = YAML()
    with yaml_path.open(encoding="utf-8") as f:
        data = yaml.load(f)

    cv = data.get("cv", {})
    strings: list[str] = []

    # Contact info
    for key in ("name", "email", "location"):
        val = cv.get(key)
        if val and len(str(val)) > 3:
            strings.append(str(val))

    sections = cv.get("sections", {})
    for entries in sections.values():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            # Core fields
            for key in (
                "company",
                "institution",
                "position",
                "title",
                "label",
                "degree",
                "area",
            ):
                val = entry.get(key)
                if val and len(str(val)) > 3:
                    strings.append(strip_markdown(str(val)))
            # Highlights / bullet points
            for highlight in entry.get("highlights", []) or []:
                text = strip_markdown(str(highlight))
                if len(text) > 10:
                    strings.append(text)

    return strings


def check_garbled(text: str) -> list[str]:
    """Check for garbled/replacement characters in extracted text."""
    issues: list[str] = []
    for pattern in GARBLED_PATTERNS:
        if pattern in text:
            issues.append(f"Found garbled: {pattern!r}")
    return issues


def compute_accuracy(extracted: str, expected_strings: list[str]) -> dict:
    """Compute extraction accuracy against expected strings."""
    if not expected_strings:
        return {"found": 0, "total": 0, "accuracy": 1.0, "missing": []}

    normalized = normalize_quotes(" ".join(extracted.split()))
    found = 0
    missing: list[str] = []

    for s in expected_strings:
        ns = normalize_quotes(" ".join(s.split()))
        if ns in normalized:
            found += 1
        else:
            missing.append(s)

    return {
        "found": found,
        "total": len(expected_strings),
        "accuracy": found / len(expected_strings),
        "missing": missing[:10],
    }


def conformance_level(f1: float) -> str:
    """Determine conformance level label from F1 score."""
    if f1 >= 0.95:
        return "Supports"
    if f1 >= 0.80:
        return "Partially Supports"
    return "Does Not Support"


def load_json(path: Path) -> dict:
    """Load a JSON file, return empty dict if not found."""
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: dict | list) -> None:
    """Write data as JSON, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_ground_truth(yaml_path: Path) -> dict:
    """Load structured ground truth directly from a corpus YAML file.

    Returns a flat dict with contact info, work entries, education entries,
    and skills — everything needed to evaluate commercial parser accuracy.
    """
    yaml = YAML()
    with yaml_path.open(encoding="utf-8") as f:
        data = yaml.load(f)

    cv = data.get("cv", {})
    sections = cv.get("sections", {})

    gt: dict = {
        "name": cv.get("name", ""),
        "email": str(cv.get("email", "")),
        "phone": str(cv.get("phone", "")),
        "location": cv.get("location", ""),
        "work": [],
        "education": [],
        "skills": [],
    }

    for section_name, entries in sections.items():
        key = section_name.lower().replace(" ", "_")
        if not isinstance(entries, list):
            continue

        if key in EXPERIENCE_SECTION_NAMES:
            for e in entries:
                if not isinstance(e, dict) or "company" not in e:
                    continue
                gt["work"].append(
                    {
                        "company": strip_markdown(e.get("company", "")),
                        "position": strip_markdown(e.get("position", "")),
                        "start_date": str(e.get("start_date", "")),
                        "end_date": str(e.get("end_date", "")),
                    }
                )

        elif key in EDUCATION_SECTION_NAMES:
            for e in entries:
                if not isinstance(e, dict) or "institution" not in e:
                    continue
                gt["education"].append(
                    {
                        "institution": strip_markdown(e.get("institution", "")),
                        "degree": strip_markdown(e.get("degree", "")),
                    }
                )

        elif key in SKILLS_SECTION_NAMES:
            for e in entries:
                if not isinstance(e, dict) or "label" not in e:
                    continue
                details = e.get("details", "")
                if details:
                    gt["skills"].extend(
                        kw.strip() for kw in str(details).split(",") if kw.strip()
                    )

    return gt
