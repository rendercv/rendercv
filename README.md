<div align="center">
<h1>RenderCV</h1>

_The engine of the [RenderCV App](https://rendercv.com)_

[![test](https://github.com/rendercv/rendercv/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/rendercv/rendercv/actions/workflows/test.yaml)
[![coverage](https://coverage-badge.samuelcolvin.workers.dev/rendercv/rendercv.svg)](https://coverage-badge.samuelcolvin.workers.dev/redirect/rendercv/rendercv)
[![docs](<https://img.shields.io/badge/docs-mkdocs-rgb(0%2C79%2C144)>)](https://docs.rendercv.com)
[![pypi-version](<https://img.shields.io/pypi/v/rendercv?label=PyPI%20version&color=rgb(0%2C79%2C144)>)](https://pypi.python.org/pypi/rendercv)
[![pypi-downloads](<https://img.shields.io/pepy/dt/rendercv?label=PyPI%20downloads&color=rgb(0%2C%2079%2C%20144)>)](https://pypistats.org/packages/rendercv)

</div>

RenderCV engine is a Typst-based Python package with a command-line interface (CLI) that allows you to version-control your CV/resume as source code. It supports Markdown syntax.

RenderCV engine's focus is to provide these three features:

- **Content-first approach:** CV writers should be able to focus on the content instead of worrying about the formatting.
- **A mechanism to version-control a CV's content and design separately:** The content and design are version-controlled as a source code completely separately.
- **Robustness:** A robust system that always delivers a PDF if there aren't any errors. If there are errors, it provides clear explanations and solutions.


It takes a YAML file that looks like this:

```yaml
cv:
  name: John Doe
  location: Your Location
  email: youremail@yourdomain.com
  sections:
    this_is_a_section_title:
      - This is a type of entry, TextEntry—just a plain string.
      - You may have as many entries as you want under a section.
      - RenderCV offers a variety of entry types such as TextEntry,
        BulletEntry, EducationEntry, ExperienceEntry, NormalEntry,
        OneLineEntry, PublicationEntry.
      - Each entry type has its own set of attributes and different
        looks.
    my_education_section:
      - institution: Boğaziçi University
        area: Mechanical Engineering
        degree: BS
        start_date: 2024-09
        end_date: 2029-05
        highlights:
          - "GPA: 3.9/4.0 ([Transcript](https://example.com))"
          - "**Coursework:** Structural Analysis, Thermodynamics,
            Heat Transfer"
    experience: ...
```

Then, it produces one of these PDFs with its corresponding Typst file, Markdown file, HTML file, and images as PNGs. Click on the images below to preview PDF files.

| [![Classic Theme Example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/classic.png)](https://github.com/rendercv/rendercv/blob/main/examples/John_Doe_ClassicTheme_CV.pdf)    | [![Sb2nov Theme Example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/sb2nov.png)](https://github.com/rendercv/rendercv/blob/main/examples/John_Doe_Sb2novTheme_CV.pdf)                                     |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [![Moderncv Theme Example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/moderncv.png)](https://github.com/rendercv/rendercv/blob/main/examples/John_Doe_ModerncvTheme_CV.pdf) | [![Engineeringresumes Theme Example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/engineeringresumes.png)](https://github.com/rendercv/rendercv/blob/main/examples/John_Doe_EngineeringresumesTheme_CV.pdf) |

RenderCV comes with a JSON Schema so that the YAML input file can be filled out interactively.

![JSON Schema of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/schema.gif)

## Quick Start Guide

RenderCV engine is very easy to install (`pip install rendercv`) and easy to use (`rendercv new "John Doe"`). Follow the [user guide](https://docs.rendercv.com/user_guide) to get started.

## Motivation

We are developing a purpose-built app for writing CVs and resumes that will be available on mobile and web. This Python project is the foundation of that app. Check out [our blog post](https://rendercv.com/introducing-rendercv/) to learn more about why one would use such an app.

## Contributing

All contributions to RenderCV are welcome! To get started, please read [the developer guide](https://docs.rendercv.com/developer_guide). 
