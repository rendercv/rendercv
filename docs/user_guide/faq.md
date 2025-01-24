# Frequently Asked Questions (FAQ)

## How to use it with JSON Resume?

You can use [jsonresume-to-rendercv](https://github.com/guruor/jsonresume-to-rendercv) to convert your JSON Resume file to a RenderCV input file.

## How to use it with Docker?

RenderCV's Docker image is available [on Docker Hub](https://hub.docker.com/r/rendercv/rendercv).

If you have Docker installed, you can use RenderCV without installing anything else. Run the command below to open a Docker container with RenderCV installed.

```bash
docker run -it -v ./rendercv:/rendercv docker.io/rendercv/rendercv:latest
```

Then, you can use RenderCV CLI as if it were installed on your machine. The files will be saved in the `rendercv` directory.

## How to create a custom theme?

RenderCV is a general Typst-based CV framework. It allows you to use any Typst code to generate your CVs. To begin developing a custom theme, run the command below.

```bash
rendercv create-theme "mycustomtheme"
```

This command will create a directory called `mycustomtheme`, which contains the following files:

``` { .sh .no-copy }
├── mycustomtheme
│   ├── __init__.py
│   ├── Preamble.j2.typ
│   ├── Header.j2.typ
│   ├── EducationEntry.j2.typ
│   ├── ExperienceEntry.j2.typ
│   ├── NormalEntry.j2.typ
│   ├── OneLineEntry.j2.typ
│   ├── PublicationEntry.j2.typ
│   ├── TextEntry.j2.typ
│   ├── SectionBeginning.j2.typ
│   └── SectionEnding.j2.typ
└── Your_Full_Name_CV.yaml
```

The files are copied from the `classic` theme. You can update the contents of these files to create your custom theme.

To use your custom theme, update the `design.theme` field in the YAML input file as shown below.

```yaml
cv:
  ...

design:
  theme: mycustomtheme
```

Then, run the `render` command to render your CV with `mycustomtheme`.

!!! note
    Since JSON Schema will not recognize the name of the custom theme, it may show a warning in your IDE. This warning can be ignored.

Each of these `*.j2.typ` files is Typst code with some Python in it. These files allow RenderCV to create your CV out of the YAML input.

The best way to understand how they work is to look at the templates of the built-in themes:

- [templates of the `classic` theme](../reference/themes/classic.md#jinja-templates)

For example, the content of `ExperienceEntry.j2.typ` for the `classic` theme is shown below:

```typst
\cventry{
    ((* if design.show_only_years *))
    <<entry.date_string_only_years>>
    ((* else *))
    <<entry.date_string>>
    ((* endif *))
}{
    <<entry.position>>
}{
    <<entry.company>>
}{
    <<entry.location>>
}{}{}
((* for item in entry.highlights *))
\cvline{}{\small <<item>>}
((* endfor *))
```

The values between `<<` and `>>` are the names of Python variables, allowing you to write a Typst CV without writing any content. They will be replaced with the values found in the YAML input. The values between `((*` and `*))` are Python blocks, allowing you to use loops and conditional statements.

The process of generating Typst files like this is called "templating," and it is achieved with a Python package called [Jinja](https://jinja.palletsprojects.com/en/3.1.x/).

The `__init__.py` file found in the theme directory defines the design options of the custom theme. You can define your custom design options in this file.

For example, an `__init__.py` file is shown below:

```python
from typing import Literal

import pydantic

class YourcustomthemeThemeOptions(pydantic.BaseModel):
    theme: Literal["yourcustomtheme"]
    option1: str
    option2: str
    option3: int
    option4: bool
```

RenderCV will then parse your custom design options from the YAML input. You can use these variables inside your `*.j2.typ` files as shown below:

```typst
<<design.option1>>
<<design.option2>>
((* if design.option4 *))
    <<design.option3>>
((* endif *))
```

!!! info
    Refer [here](cli.md#rendercv-create-theme-command) for the complete list of CLI options available for the `create-theme` command.
