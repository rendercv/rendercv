"""Submit rendered PDFs to commercial resume parsers via Eden AI.

Eden AI forwards PDFs to Affinda and HireAbility and returns both results.

Requires environment variable:
  EDENAI_API_KEY — from https://app.edenai.run/user/register
"""

import os
import sys
import time
from pathlib import Path

import httpx
from common import RENDERED_DIR, RESULTS_DIR, find_rendered_pdfs, write_json

RESULTS_SUBDIR: str = "commercial/edenai"
RATE_LIMIT_SECONDS: float = 2.0


def submit(client: httpx.Client, pdf_path: Path) -> dict:
    """Submit a PDF to Eden AI's resume parser (Affinda + HireAbility)."""
    with pdf_path.open("rb") as f:
        response = client.post(
            "https://api.edenai.run/v2/ocr/resume_parser",
            files={"file": (pdf_path.name, f, "application/pdf")},
            data={"providers": "affinda,extracta,klippa"},
            timeout=90,
        )
    response.raise_for_status()
    return response.json()


def main() -> None:
    api_key = os.environ.get("EDENAI_API_KEY", "")
    if not api_key:
        print("EDENAI_API_KEY not set. Sign up at https://app.edenai.run/user/register")  # noqa: T201
        print("and create an API key at https://app.edenai.run/admin/account/settings.")  # noqa: T201
        print()  # noqa: T201
        print("Then run:")  # noqa: T201
        print("  EDENAI_API_KEY=your_key uv run python submit_commercial.py")  # noqa: T201
        sys.exit(1)

    pdfs = find_rendered_pdfs()
    if not pdfs:
        print("No PDFs found. Run render_pdfs.py first.")  # noqa: T201
        sys.exit(1)

    results_dir = RESULTS_DIR / RESULTS_SUBDIR
    results_dir.mkdir(parents=True, exist_ok=True)

    client = httpx.Client(
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=120,
    )

    success = 0
    failed = 0

    print(f"Submitting {len(pdfs)} PDFs to Eden AI (Affinda, Extracta, Klippa)...")  # noqa: T201

    try:
        for i, pdf_path in enumerate(pdfs):
            rel = pdf_path.relative_to(RENDERED_DIR)
            cache_name = "_".join(rel.parts).replace(".pdf", "") + ".json"
            output_path = results_dir / cache_name

            if output_path.exists():
                print(f"  [{i + 1}/{len(pdfs)}] SKIP (cached): {rel}")  # noqa: T201
                success += 1
                continue

            try:
                result = submit(client, pdf_path)
                write_json(output_path, result)
                success += 1
                print(f"  [{i + 1}/{len(pdfs)}] OK: {rel}")  # noqa: T201
                time.sleep(RATE_LIMIT_SECONDS)

            except httpx.HTTPStatusError as e:
                failed += 1
                print(f"  [{i + 1}/{len(pdfs)}] FAIL ({e.response.status_code}): {rel}")  # noqa: T201
                if e.response.status_code == 429:
                    print("    Rate limited. Waiting 30s...")  # noqa: T201
                    time.sleep(30)
            except Exception as e:
                failed += 1
                print(f"  [{i + 1}/{len(pdfs)}] ERROR: {rel} - {e}")  # noqa: T201
    finally:
        client.close()

    print(f"\nDone. {success} succeeded, {failed} failed.")  # noqa: T201


if __name__ == "__main__":
    main()
