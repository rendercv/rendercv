# The engine of the [RenderCV App](https://rendercv.com)

[![test](https://github.com/rendercv/rendercv/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/rendercv/rendercv/actions/workflows/test.yaml)
[![coverage](https://coverage-badge.samuelcolvin.workers.dev/rendercv/rendercv.svg)](https://coverage-badge.samuelcolvin.workers.dev/redirect/rendercv/rendercv)
[![docs](https://img.shields.io/badge/docs-mkdocs-rgb(0%2C79%2C144))](https://docs.rendercv.com)
[![pypi-version](https://img.shields.io/pypi/v/rendercv?label=PyPI%20version&color=rgb(0%2C79%2C144))](https://pypi.python.org/pypi/rendercv)
[![pypi-downloads](https://img.shields.io/pepy/dt/rendercv?label=PyPI%20downloads&color=rgb(0%2C%2079%2C%20144))](https://pypistats.org/packages/rendercv)

Write your CV or resume as YAML, then call RenderCV:

```bash
rendercv render John_Doe_CV.yaml
```

and get a PDF with professional typography. No template wrestling. No broken layouts. Consistent spacing, every time.

With RenderCV, you can:

- Version-control your CV/resume as source code.
- Focus on the content, without worrying about the formatting.

A YAML file that looks like this:

```yaml
cv:
  name: John Doe
  headline:
  location: San Francisco, CA
  email: john.doe@email.com
  photo:
  phone:
  website: https://rendercv.com/
  social_networks:
    - network: LinkedIn
      username: rendercv
    - network: GitHub
      username: rendercv
  sections:
    Welcome to RenderCV:
      - RenderCV reads a CV written in a YAML file, and generates a PDF with professional typography.
      - See the [documentation](https://docs.rendercv.com) for more details.
    education:
      - institution: Princeton University
        area: Computer Science
        degree: PhD
        date:
        start_date: 2018-09
        end_date: 2023-05
        location: Princeton, NJ
        summary:
        highlights:
          - "Thesis: Efficient Neural Architecture Search for Resource-Constrained Deployment"
          - "Advisor: Prof. Sanjeev Arora"
          - NSF Graduate Research Fellowship, Siebel Scholar (Class of 2022)
    ...
```

becomes one of these PDFs. Click on the images below to preview PDF files.

| [![Classic Theme Example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/classic.png)](https://github.com/rendercv/rendercv/blob/main/examples/John_Doe_ClassicTheme_CV.pdf)                                  | [![Engineeringresumes Theme Example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/engineeringresumes.png)](https://github.com/rendercv/rendercv/blob/main/examples/John_Doe_EngineeringresumesTheme_CV.pdf) |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [![Sb2nov Theme Example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/sb2nov.png)](https://github.com/rendercv/rendercv/blob/main/examples/John_Doe_Sb2novTheme_CV.pdf)                                     | [![Moderncv Theme Example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/moderncv.png)](https://github.com/rendercv/rendercv/blob/main/examples/John_Doe_ModerncvTheme_CV.pdf)                               |
| [![Engineeringclassic Theme Example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/engineeringclassic.png)](https://github.com/rendercv/rendercv/blob/main/examples/John_Doe_EngineeringclassicTheme_CV.pdf) | ![Custom themes can be added.](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/customtheme.png)                                                                                                                            |

## JSON Schema

RenderCV comes with a JSON Schema so that the YAML input file can be filled out interactively.

![JSON Schema of RenderCV](./assets/images/json_schema.gif)


## Extensive Design Options

You can almost achieve any design you want by playing with the design options.

```yaml
design:
  theme: classic
  page:
    size: us-letter
    top_margin: 0.7in
    bottom_margin: 0.7in
    left_margin: 0.7in
    right_margin: 0.7in
    show_footer: true
    show_top_note: true
  colors:
    body: rgb(0, 0, 0)
    name: rgb(0, 79, 144)
    headline: rgb(0, 79, 144)
    connections: rgb(0, 79, 144)
    section_titles: rgb(0, 79, 144)
    links: rgb(0, 79, 144)
    footer: rgb(128, 128, 128)
    top_note: rgb(128, 128, 128)
  typography:
    line_spacing: 0.6em
    alignment: justified
    date_and_location_column_alignment: right
    font_family: Source Sans 3
  ...
  # It goes on and on...
```

![Design Options of RenderCV](./assets/images/design_options.gif)

## Strict Validation

No surprises. If something's wrong, you'll know exactly what and where. If it's valid, you get a perfect PDF.

![Strict Validation Feature of RenderCV](./assets/images/validation.gif)


## Get Started

Install Python 3.12 or newer. Then, run the command below to install RenderCV.

```
pip install "rendercv[full]"
```

Then, run the command below to create a new CV.

```
rendercv new "John Doe"
```

Then, edit your YAML file, and render it.

```
rendercv render "John_Doe_CV.yaml"
```

For more details, see the [user guide](user_guide/get_started.md).