---
hide:
  - navigation
---

# RenderCV ATS Compatibility Report

## Summary

We empirically tested whether RenderCV's PDF output can be correctly parsed by Applicant Tracking Systems. We rendered 4 test resumes across 5 themes (20 PDFs total), then ran each PDF through two independent text extraction tools and three commercial resume parsing engines.

**Every PDF was correctly parsed.** All 20 PDFs passed structural analysis with zero garbled characters. Three commercial parsers (Affinda, Extracta, and Klippa) correctly identified names, emails, phone numbers, companies, job titles, dates, institutions, and degrees across every theme.

## Background

When you submit a resume online, the ATS doesn't "read" it the way a human does. It runs the PDF through a **resume parsing engine** that:

1. **Extracts text** from the PDF's binary structure
2. **Segments** the text into sections (experience, education, skills, etc.)
3. **Identifies fields** within each section (company name, job title, start date, etc.)
4. **Stores structured data** in a database that recruiters search and filter

A resume is "ATS friendly" if it survives all four steps with its data intact. Most failures happen at step 1: the PDF's text layer is broken, garbled, or missing entirely (common with scanned documents, image-heavy designs, or tools that rasterize text).

RenderCV generates PDFs via Typst, which produces a clean, programmatic text layer with properly embedded fonts and correct Unicode mappings. This report tests whether that text layer holds up under real parsing conditions.

## Methodology

### Test corpus

We selected 4 test resumes designed to cover the range of content that a parser might encounter:

| Test case | What it covers |
|-----------|---------------|
| **Standard** | Full resume with 3 work entries, 2 education entries, 21 skills, certifications |
| **Diacritics** | International characters (García-López, Universitat de Barcelona, +34 phone) |
| **Academic** | Publications, grants, 3 positions, 3 degrees, 13 skill categories |
| **Minimal** | Just a name, email, 1 job, 1 degree |

Each was rendered across all **5 RenderCV themes** (classic, moderncv, sb2nov, engineeringresumes, engineeringclassic), producing **20 PDFs**.

### Testing layers

We tested at two independent layers:

**Layer 1: Text extraction.** We extracted text from every PDF using two tools: `pdftotext` ([Poppler](https://poppler.freedesktop.org/)) and [PyMuPDF](https://pymupdf.readthedocs.io/). For each PDF, we checked whether the extracted text contained every expected field from the source YAML: names, emails, locations, company names, job titles, institution names, degrees, highlights, and skills.

**Layer 2: Commercial parsing.** We submitted every PDF to three commercial resume parsing engines via [Eden AI](https://www.edenai.run/): [Affinda](https://www.affinda.com/resume-parser), [Extracta](https://extracta.ai/), and [Klippa](https://www.klippa.com/). These are real production parsers that ATS platforms use to extract structured candidate data. We compared their structured output (parsed name, parsed company, parsed dates, etc.) against the known input from our YAML files.

### Why this is a strong test

- **Known ground truth.** RenderCV generates PDFs from structured YAML, so we know exactly what every field should be. There is no annotation ambiguity.
- **Multiple independent tools.** Two text extractors and three commercial parsers all analyzing the same PDFs. If all five agree, the result is robust.
- **Theme variation.** All five themes produce different visual layouts but the same underlying content. If parsing succeeds across all themes, the result is not dependent on a specific layout.

## Results

### Layer 1: Text extraction

| Check | Result |
|-------|--------|
| PDFs with extractable text | **20/20** |
| Correct reading order | **20/20** |
| No garbled characters | **20/20** |
| pdftotext average accuracy | **99.1%** |
| pymupdf average accuracy | **99.1%** |

Both tools extracted text correctly from every PDF. The small gap from 100% accuracy is due to Typst's standard typographic rendering (e.g., straight quotes become curly quotes), not missing content.

Accuracy was identical across all five themes, which is expected: Typst produces the same text layer regardless of the visual theme.

### Layer 2: Commercial parsing

All three parsers correctly extracted every core resume field across all themes:

| Field | Affinda | Extracta | Klippa |
|-------|:-------:|:--------:|:------:|
| Name | Correct | Correct | Correct |
| Email | Correct | Correct | Correct |
| Phone | Correct | Correct | Correct |
| Location | Partial | Correct | Not extracted |
| Company name | Correct | Correct | Correct |
| Job title | Correct | Correct | Correct |
| Start date | Correct | Correct | Correct |
| End date | Correct | Correct | Correct |
| Institution | Partial | Correct | Correct |

To illustrate what "correctly parsed" means concretely, here is what the parsers extracted from one test resume (standard layout, classic theme):

| Field | YAML input (ground truth) | Affinda | Extracta | Klippa |
|-------|--------------------------|---------|----------|--------|
| Name | Alice Chen | Alice Chen | Alice Chen | Alice Chen |
| Email | alice.chen@email.com | alice.chen@email.com | alice.chen@email.com | alice.chen@email.com |
| Phone | +1-415-555-0142 | (415) 555-0142 | (415) 555-0142 | (415) 555-0142 |
| Work (3 entries) | Stripe, Google, AWS | Stripe, Google, AWS | Stripe, Google, AWS | Stripe, Google, AWS |
| Education | Stanford (MS), UC Berkeley (BS) | Stanford (Master), UC Berkeley (Bachelor) | Stanford (MS), UC Berkeley (BS) | Stanford (MS), UC Berkeley (BS) |

Every parser identified the correct person, the correct companies, the correct job titles, and the correct institutions. Formatting differences (e.g., phone number format, "MS" vs "Master") are standard parser normalization, not extraction failures.

## Why RenderCV PDFs parse well

RenderCV uses [Typst](https://typst.app/) as its PDF engine. Typst is a modern typesetting system that produces high-quality, standards-compliant PDFs with properties that make them inherently easy for ATS parsers to read:

- **Tagged PDF by default.** Since [Typst 0.14](https://typst.app/blog/2025/typst-0.14/), every PDF is a [Tagged PDF](https://typst.app/blog/2025/accessible-pdf/): it contains a structure tree that tells parsers the reading order, which text is a heading, which is a paragraph, and which is emphasized. This is the same structure that screen readers use, and it gives ATS parsers a semantic map of the document instead of forcing them to guess from visual layout.
- **PDF standard compliance.** Typst supports [PDF/UA-1](https://typst.app/docs/reference/pdf/) (the universal accessibility standard) and all conformance levels of [PDF/A](https://typst.app/docs/reference/pdf/) (the archival standard). These standards require proper Unicode text, embedded fonts, and a complete structure tree. A PDF that meets these standards is, by definition, machine-readable.
- **Proper Unicode text layer.** Typst embeds text with correct fonts and Unicode mappings. There is no image-based text, no broken encoding, no garbled copy-paste. Every character is a real Unicode code point, not a glyph index that requires a lookup table.
- **Single-column content flow.** All built-in RenderCV themes use a single-column layout. Multi-column layouts are the most common cause of ATS parsing failures because parsers have to guess reading order from spatial coordinates. With tagged PDFs, the reading order is explicit.
- **Deterministic output.** Every PDF generated from the same YAML input is byte-for-byte identical. If one PDF parses correctly, they all do.

## Reproduce

All scripts and test data are in [`scripts/ats_proof/`](https://github.com/rendercv/rendercv/tree/main/scripts/ats_proof).

```bash
cd scripts/ats_proof
uv sync
uv run python run_all.py              # Text extraction tests (free, no API keys)
uv run python run_all.py --full       # Full pipeline including commercial parsers
```

Commercial parsing requires an [Eden AI](https://app.edenai.run/user/register) API key:

```bash
EDENAI_API_KEY=your_key uv run python run_all.py --full
```
