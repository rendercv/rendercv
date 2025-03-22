<div align="center">
<h1>RenderCV</h1>

_The engine of the [RenderCV App](https://rendercv.com)_

[![test](https://github.com/rendercv/rendercv/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/rendercv/rendercv/actions/workflows/test.yaml)
[![coverage](https://coverage-badge.samuelcolvin.workers.dev/rendercv/rendercv.svg)](https://coverage-badge.samuelcolvin.workers.dev/redirect/rendercv/rendercv)
[![docs](<https://img.shields.io/badge/docs-mkdocs-rgb(0%2C79%2C144)>)](https://docs.rendercv.com)
[![pypi-version](<https://img.shields.io/pypi/v/rendercv?label=PyPI%20version&color=rgb(0%2C79%2C144)>)](https://pypi.python.org/pypi/rendercv)
[![pypi-downloads](<https://img.shields.io/pepy/dt/rendercv?label=PyPI%20downloads&color=rgb(0%2C%2079%2C%20144)>)](https://pypistats.org/packages/rendercv)

</div>

RenderCV engine is a Typst-based Python package with a command-line interface (CLI) that allows you to version-control your CV/resume as source code. It reads a CV written in a YAML file with Markdown syntax, converts it into a [Typst](https://typst.app) code, and generates a PDF.

RenderCV engine's focus is to provide these three features:

- **Content-first approach:** Users should be able to focus on the content instead of worrying about the formatting.
- **A mechanism to version-control a CV's content and design separately:** The content and design of a CV are separate issues and they should be treated separately.
- **Robustness:** A PDF should be delivered if there aren't any errors. If errors exist, they should be clearly explained along with solutions.


It takes a YAML file that looks like this:

```yaml
cv:
  name: John Doe
  location: Location
  email: john.doe@example.com
  phone: tel:+1-609-999-9995
  social_networks:
    - network: LinkedIn
      username: john.doe
    - network: GitHub
      username: john.doe
  sections:
    welcome_to_RenderCV!:
      - '[RenderCV](https://rendercv.com) is a Typst-based CV
        framework designed for academics and engineers, with Markdown
        syntax support.'
      - Each section title is arbitrary. Each section contains
        a list of entries, and there are 7 different entry types
        to choose from.
    education:
      - institution: Stanford University
        area: Computer Science
        degree: PhD
        location: Stanford, CA, USA
        start_date: 2023-09
        end_date: present
        highlights:
          - Working on the optimization of autonomous vehicles
            in urban environments
    ...
```

Then, it produces one of these PDFs with its corresponding Typst file, Markdown file, HTML file, and images as PNGs. Click on the images below to preview PDF files.

| [![Classic Theme Example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/classic.png)](https://github.com/rendercv/rendercv/blob/main/examples/John_Doe_ClassicTheme_CV.pdf)    | [![Sb2nov Theme Example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/sb2nov.png)](https://github.com/rendercv/rendercv/blob/main/examples/John_Doe_Sb2novTheme_CV.pdf)                                     |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [![Moderncv Theme Example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/moderncv.png)](https://github.com/rendercv/rendercv/blob/main/examples/John_Doe_ModerncvTheme_CV.pdf) | [![Engineeringresumes Theme Example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/engineeringresumes.png)](https://github.com/rendercv/rendercv/blob/main/examples/John_Doe_EngineeringresumesTheme_CV.pdf) |
| [![Engineeringclassic Theme Example of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/engineeringclassic.png)](https://github.com/rendercv/rendercv/blob/main/examples/John_Doe_EngineeringclassicTheme_CV.pdf) | ![Custom themes can be added.](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/customtheme.png) |

RenderCV comes with a JSON Schema so that the YAML input file can be filled out interactively.

![JSON Schema of RenderCV](https://raw.githubusercontent.com/rendercv/rendercv/main/docs/assets/images/schema.gif)

## Getting Started

RenderCV engine is very easy to install (`pip install "rendercv[full]"`) and easy to use (`rendercv new "John Doe"`). Follow the [user guide](https://docs.rendercv.com/user_guide) to get started.

## Motivation

We are developing a [purpose-built app](https://rendercv.com) for writing CVs and resumes that will be available on mobile and web. This Python project is the foundation of that app. Check out [our blog post](https://rendercv.com/introducing-rendercv/) to learn more about why one would use such an app.

## Contributing

All contributions to RenderCV are welcome! To get started, please read [the developer guide](https://docs.rendercv.com/developer_guide). 
