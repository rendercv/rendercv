# User Guide

This page provides everything you need to know about the usage of RenderCV.

## Installation

1. Install [Python](https://www.python.org/downloads/) (3.10 or newer).

2. Run the command below to install RenderCV.

```bash
pip install rendercv
```

## Getting started

To get started, navigate to the directory where you want to create your CV and run the command below to create the input files.

```bash
rendercv new "Your Full Name"
```
This command will create the following files:

-   A YAML input file called `Your_Name_CV.yaml`.

    This file contains the content and design options of your CV. A detailed explanation of the structure of the YAML input file is provided [here](structure_of_the_yaml_input_file.md).

-   A directory called `classic`.

    This directory contains the Typst templates of RenderCV's default built-in theme, `classic`. You can update its contents to tweak the appearance of the output PDF file.

-   A directory called `markdown`.

    This directory contains the templates of RenderCV's default Markdown template. You can update its contents to tweak the Markdown and HTML output of the CV.

!!! info    
    Refer to the [here](cli.md#rendercv-new-command) for the complete list of CLI options available for the `new` command.

Then, open the `Your_Name_CV.yaml` file in your favorite text editor and fill it with your information. See the [structure of the YAML input file](structure_of_the_yaml_input_file.md) for more information about the YAML input file.

Finally, render the YAML input file to generate your CV.

```bash
rendercv render "Your_Name_CV.yaml"
```

This command will generate a directory called `rendercv_output`, which contains the following files:

-   The CV in PDF format, `Your_Name_CV.pdf`.
-   Typst source code of the PDF file, `Your_Name_CV.typ`.
-   Images of each page of the PDF file in PNG format, `Your_Name_CV_1.png`, `Your_Name_CV_page_2.png`, etc.
-   The CV in Markdown format, `Your_Name_CV.md`.
-   The CV in HTML format, `Your_Name_CV.html`. You can open this file in a web browser and copy-paste the content to Grammarly for proofreading.

!!! info
    Refer to the [here](cli.md#rendercv-render-command) for the complete list of CLI options available for the `render` command.

## Overriding built-in themes

If the theme and Markdown templates are found in the directory, they will override the default built-in theme and Markdown templates. You don't need to provide all the files; you can just provide the ones you want to override.

For example, `ExperienceEntry` of the `classic` theme can be modified as shown below.

``` { .sh .no-copy }
├── classic
│   └── ExperienceEntry.j2.typ # (1)!
└── Your_Full_Name_CV.yaml
```

1.  This file will override the built-in `ExperienceEntry.j2.typ` template of the `classic` theme.


## Creating custom themes with the `create-theme` command

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
- [templates of the `engineeringresumes` theme](../reference/themes/engineeringresumes.md#jinja-templates)
- [templates of the `sb2nov` theme](../reference/themes/sb2nov.md#jinja-templates)

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
