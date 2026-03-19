"""Evaluate commercial parser results against ground truth from corpus YAML.

Computes precision, recall, and F1 per field, generates summary tables
for the report. Ground truth is read directly from the corpus YAML files.
"""

import re
from collections import defaultdict
from pathlib import Path

from common import (
    ANALYSIS_DIR,
    CORPUS_DIR,
    RESULTS_DIR,
    conformance_level,
    load_ground_truth,
    load_json,
    write_json,
)


# ---------------------------------------------------------------------------
# Matching functions
# ---------------------------------------------------------------------------


def normalize(text: str) -> str:
    """Normalize text for comparison."""
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s@.+\-/]", "", text)
    return text


def exact_match(expected: str, extracted: str) -> float:
    """Exact match after normalization."""
    return 1.0 if normalize(expected) == normalize(extracted) else 0.0


def phone_match(expected: str, extracted: str) -> float:
    """Compare phone numbers by digits only (ignore formatting)."""
    expected_digits = re.sub(r"\D", "", expected)
    extracted_digits = re.sub(r"\D", "", extracted)
    if not expected_digits or not extracted_digits:
        return 0.0
    # Match if one contains the other (country code may be stripped)
    if expected_digits.endswith(extracted_digits) or extracted_digits.endswith(
        expected_digits
    ):
        return 1.0
    return 1.0 if expected_digits == extracted_digits else 0.0


def fuzzy_match(expected: str, extracted: str, threshold: float = 0.9) -> float:
    """Token overlap match."""
    expected_tokens = set(normalize(expected).split())
    extracted_tokens = set(normalize(extracted).split())
    if not expected_tokens:
        return 1.0 if not extracted_tokens else 0.0
    overlap = expected_tokens & extracted_tokens
    precision = len(overlap) / len(extracted_tokens) if extracted_tokens else 0
    recall = len(overlap) / len(expected_tokens)
    if precision + recall == 0:
        return 0.0
    f1 = 2 * precision * recall / (precision + recall)
    return f1 if f1 >= threshold else 0.0


def date_match(expected: str, extracted: str) -> float:
    """Normalize dates and compare (year-month only, handles 'present')."""
    month_map = {
        "jan": "01",
        "feb": "02",
        "mar": "03",
        "apr": "04",
        "may": "05",
        "jun": "06",
        "june": "06",
        "jul": "07",
        "july": "07",
        "aug": "08",
        "sep": "09",
        "sept": "09",
        "oct": "10",
        "nov": "11",
        "dec": "12",
    }

    def parse(d: str) -> str:
        d = d.strip().lower()
        if not d or d == "present":
            return "present"
        for name, num in month_map.items():
            d = d.replace(name, num)
        digits = re.findall(r"\d+", d)
        # Keep only year and month (ignore day)
        return "-".join(digits[:2]) if digits else d

    expected_parsed = parse(expected)
    extracted_parsed = parse(extracted)

    # "present" in GT matches any current/recent date or "present"
    if expected_parsed == "present":
        return 1.0

    return 1.0 if expected_parsed == extracted_parsed else 0.0


def jaccard(expected: list[str], extracted: list[str]) -> float:
    """Jaccard similarity for unordered lists."""
    a = {normalize(s) for s in expected}
    b = {normalize(s) for s in extracted}
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# ---------------------------------------------------------------------------
# Field extraction from parser results
# ---------------------------------------------------------------------------


def extract_fields_edenai(result: dict, provider: str) -> dict:
    """Extract standardized fields from Eden AI response."""
    data = result.get(provider, {}).get("extracted_data", {})
    if not data:
        return {}

    fields: dict = {}
    personal = data.get("personal_infos", {}) or {}
    if personal.get("name", {}).get("raw_name"):
        fields["name"] = personal["name"]["raw_name"]
    if personal.get("phones"):
        fields["phone"] = str(personal["phones"][0])
    if personal.get("mails"):
        fields["email"] = personal["mails"][0]
    address = personal.get("address") or {}
    location = address.get("raw_input_location") or address.get("formatted_location")
    if location:
        fields["location"] = location

    fields["work"] = []
    for entry in data.get("work_experience", {}).get("entries", []) or []:
        w: dict = {}
        if entry.get("company"):
            w["company"] = entry["company"]
        if entry.get("title"):
            w["position"] = entry["title"]
        if entry.get("start_date"):
            w["start_date"] = entry["start_date"]
        if entry.get("end_date"):
            w["end_date"] = entry["end_date"]
        if w:
            fields["work"].append(w)

    fields["education"] = []
    for entry in data.get("education", {}).get("entries", []) or []:
        e: dict = {}
        if entry.get("establishment"):
            e["institution"] = entry["establishment"]
        if entry.get("title"):
            e["degree"] = entry["title"]
        if e:
            fields["education"].append(e)

    skills_raw = data.get("skills") or []
    if isinstance(skills_raw, dict):
        skills_raw = skills_raw.get("entries", []) or []
    fields["skills"] = [
        s.get("name", "") for s in skills_raw if isinstance(s, dict) and s.get("name")
    ]
    return fields


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def degree_match(expected: str, extracted: str) -> float:
    """Match degree abbreviations to full names."""
    abbreviations: dict[str, set[str]] = {
        "bs": {"bachelor", "bachelors", "b.s.", "bsc"},
        "ba": {"bachelor", "bachelors", "b.a."},
        "ms": {"master", "masters", "m.s.", "msc"},
        "ma": {"master", "masters", "m.a."},
        "phd": {"phd", "ph.d.", "doctor", "doctorate", "doctoral"},
        "mba": {"mba", "master"},
        "mph": {"mph", "master"},
    }
    e_norm = normalize(expected)
    x_norm = normalize(extracted)
    if e_norm == x_norm:
        return 1.0
    # Check if abbreviation matches full name
    for abbrev, expansions in abbreviations.items():
        if e_norm == abbrev and any(exp in x_norm for exp in expansions):
            return 1.0
        if x_norm == abbrev and any(exp in e_norm for exp in expansions):
            return 1.0
    return fuzzy_match(expected, extracted)


def score_contact(gt: dict, extracted: dict) -> dict[str, float]:
    """Score contact fields."""
    scores: dict[str, float] = {}
    for field in ("name", "email"):
        gt_val = gt.get(field, "")
        ex_val = extracted.get(field, "")
        if gt_val:
            scores[field] = (
                fuzzy_match(gt_val, ex_val)
                if field == "name"
                else exact_match(gt_val, ex_val)
            )
    if gt.get("phone"):
        scores["phone"] = phone_match(gt["phone"], extracted.get("phone", ""))
    if gt.get("location"):
        # Lower threshold for location — parsers often add/remove country name
        scores["location"] = fuzzy_match(
            gt["location"], extracted.get("location", ""), threshold=0.7
        )
    return scores


def score_list_entries(
    gt_entries: list[dict],
    ex_entries: list[dict],
    match_fields: list[tuple[str, str]],
) -> dict[str, float]:
    """Score list entries (work/education) by best-match pairing.

    match_fields: list of (field_name, match_type) tuples where match_type
    is "fuzzy" or "date". The same field name is used in both gt and extracted.
    """
    scores: dict[str, list[float]] = defaultdict(list)
    for gt_entry in gt_entries:
        best: dict[str, float] = {}
        for ex_entry in ex_entries:
            match: dict[str, float] = {}
            for field_name, match_type in match_fields:
                if gt_entry.get(field_name):
                    gt_val = gt_entry[field_name]
                    ex_val = ex_entry.get(field_name, "")
                    if match_type == "fuzzy":
                        match[field_name] = fuzzy_match(gt_val, ex_val)
                    elif match_type == "date":
                        match[field_name] = date_match(gt_val, ex_val)
                    elif match_type == "degree":
                        match[field_name] = degree_match(gt_val, ex_val)
            avg = sum(match.values()) / len(match) if match else 0
            best_avg = sum(best.values()) / len(best) if best else 0
            if avg > best_avg:
                best = match
        for field, score in best.items():
            scores[field].append(score)
    return {f: sum(v) / len(v) for f, v in scores.items()}


def find_yaml_for_result(result_stem: str) -> Path | None:
    """Find the corpus YAML corresponding to a commercial parser result file."""
    # Result files are named like: classic_baseline_standard_full.json
    # We need the YAML stem, which is the part after theme_category_
    for subdir in sorted(CORPUS_DIR.iterdir()):
        if not subdir.is_dir():
            continue
        for yaml_path in subdir.glob("*.yaml"):
            if yaml_path.stem in result_stem:
                return yaml_path
    return None


def evaluate_parser(results_dir: Path, parser_name: str) -> dict:
    """Evaluate all results for a single parser against corpus YAML."""
    all_scores: dict[str, list[float]] = defaultdict(list)
    result_files = sorted(results_dir.glob("*.json"))
    if not result_files:
        return {}

    for result_path in result_files:
        yaml_path = find_yaml_for_result(result_path.stem)
        if not yaml_path:
            continue

        gt = load_ground_truth(yaml_path)
        raw = load_json(result_path)

        if not parser_name.startswith("edenai_"):
            continue
        extracted = extract_fields_edenai(raw, parser_name.replace("edenai_", ""))

        if not extracted:
            continue

        for field, score in score_contact(gt, extracted).items():
            all_scores[f"contact_{field}"].append(score)

        if gt["work"]:
            work_scores = score_list_entries(
                gt["work"],
                extracted.get("work", []),
                [
                    ("company", "fuzzy"),
                    ("position", "fuzzy"),
                    ("start_date", "date"),
                    ("end_date", "date"),
                ],
            )
            for field, score in work_scores.items():
                all_scores[f"work_{field}"].append(score)

        if gt["education"]:
            edu_scores = score_list_entries(
                gt["education"],
                extracted.get("education", []),
                [("institution", "fuzzy"), ("degree", "degree")],
            )
            for field, score in edu_scores.items():
                all_scores[f"edu_{field}"].append(score)

        if gt["skills"]:
            all_scores["skills"].append(
                jaccard(gt["skills"], extracted.get("skills", []))
            )

    if not all_scores:
        return {}

    averages = {f: sum(v) / len(v) for f, v in all_scores.items()}
    all_values = list(averages.values())
    overall = sum(all_values) / len(all_values) if all_values else 0.0

    return {
        "parser": parser_name,
        "per_field": averages,
        "overall_f1": overall,
        "num_evaluated": len(result_files),
    }


def main() -> None:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    evaluations: list[dict] = []

    parsers = [
        ("edenai_affinda", "commercial/edenai"),
        ("edenai_extracta", "commercial/edenai"),
        ("edenai_klippa", "commercial/edenai"),
    ]
    for parser_name, subdir in parsers:
        parser_dir = RESULTS_DIR / subdir
        if parser_dir.exists() and list(parser_dir.glob("*.json")):
            result = evaluate_parser(parser_dir, parser_name)
            if result:
                evaluations.append(result)
                print(f"{parser_name}: Overall F1 = {result['overall_f1']:.1%}")  # noqa: T201

    # Print local results for context
    struct = load_json(RESULTS_DIR / "structural" / "structural_summary.json")
    if struct:
        print(f"\nStructural: {struct.get('pass_rate', 'N/A')} pass rate")  # noqa: T201

    extraction = load_json(RESULTS_DIR / "opensource" / "extraction_summary.json")
    if extraction:
        for name, stats in extraction.get("extractors", {}).items():
            print(f"Extraction ({name}): {stats['average_accuracy']}")  # noqa: T201

    # Build output
    output: dict = {"evaluations": evaluations, "conformance_table": {}}
    if evaluations:
        all_fields: dict[str, list[float]] = defaultdict(list)
        for e in evaluations:
            for field, score in e["per_field"].items():
                all_fields[field].append(score)

        for field, scores in all_fields.items():
            avg = sum(scores) / len(scores)
            output["conformance_table"][field] = {
                "f1": avg,
                "level": conformance_level(avg),
            }

        overall_scores = [e["overall_f1"] for e in evaluations]
        overall_avg = sum(overall_scores) / len(overall_scores)
        output["overall"] = {"f1": overall_avg, "level": conformance_level(overall_avg)}
        print(f"\nOverall F1: {overall_avg:.1%} ({conformance_level(overall_avg)})")  # noqa: T201

    if not evaluations:
        print("\nNo commercial parser results. Run submit_commercial.py first.")  # noqa: T201

    write_json(ANALYSIS_DIR / "evaluation_results.json", output)
    print(f"Results saved to {ANALYSIS_DIR / 'evaluation_results.json'}")  # noqa: T201


if __name__ == "__main__":
    main()
