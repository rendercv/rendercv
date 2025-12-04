# CV Repository

This repository contains my CV/resume, version-controlled as source code using [RenderCV](https://rendercv.com).

## Overview

The CV content is stored in `cv.yaml` using the RenderCV format. A GitHub Actions workflow automatically generates a PDF whenever the CV is updated.

## Structure

- `cv.yaml` - The CV content in YAML format
- `examples/` - Generated PDF files

## Usage

### Local Development

To generate the PDF locally:

```bash
pip install "rendercv[full]"
rendercv render cv.yaml
```

The generated PDF will be in the `rendercv_output/` directory.

### Automated Generation

The CV PDF is automatically generated and updated in the `examples/` folder whenever `cv.yaml` is pushed to the main branch, thanks to the GitHub Actions workflow.

## About RenderCV

RenderCV is a Typst-based CV/resume framework that allows you to:
- Focus on content instead of formatting
- Version-control CV content and design separately
- Generate professional PDFs automatically

For more information, visit [rendercv.com](https://rendercv.com) or check out the [documentation](https://docs.rendercv.com).
