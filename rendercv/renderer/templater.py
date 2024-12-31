"""
The `rendercv.renderer.templater` module contains all the necessary classes and
functions for templating the $\\LaTeX$ and Markdown files from the `RenderCVDataModel`
object.
"""

import copy
import pathlib
import re
from collections.abc import Callable
from datetime import date as Date
from typing import Any, Literal, Optional

import jinja2

from .. import data


class TemplatedFile:
    """This class is a base class for `LaTeXFile`, `TypstFile`, and `MarkdownFile`
    classes. It contains the common methods and attributes for both classes. These
    classes are used to generate the $\\LaTeX$ and Markdown files with the data model
    and Jinja2 templates.

    Args:
        data_model: The data model.
        environment: The Jinja2 environment.
    """

    def __init__(
        self,
        data_model: data.RenderCVDataModel,
        environment: jinja2.Environment,
    ):
        self.cv = data_model.cv
        self.design = data_model.design
        self.locale_catalog = data_model.locale_catalog
        self.environment = environment

    def template(
        self,
        theme_name: str,
        template_name: str,
        extension: str,
        entry: Optional[data.Entry] = None,
        **kwargs,
    ) -> str:
        """Template one of the files in the `themes` directory.

        Args:
            template_name: The name of the template file.
            entry: The title of the section.

        Returns:
            The templated file.
        """
        template = self.environment.get_template(
            f"{theme_name}/{template_name}.j2.{extension}"
        )

        # Loop through the entry attributes and make them "" if they are None:
        # This is necessary because otherwise they will be templated as "None" since
        # it's the string representation of None.

        # Only don't touch the date fields, because only date_string is called and
        # setting dates to "" will cause problems.
        fields_to_ignore = ["start_date", "end_date", "date"]

        if entry is not None and not isinstance(entry, str):
            entry_dictionary = entry.model_dump()
            for key, value in entry_dictionary.items():
                if value is None and key not in fields_to_ignore:
                    entry.__setattr__(key, "")

        # The arguments of the template can be used in the template file:
        return template.render(
            cv=self.cv,
            design=self.design,
            locale_catalog=self.locale_catalog,
            entry=entry,
            today=data.format_date(Date.today()),
            **kwargs,
        )

    def get_full_code(self, main_template_name: str, **kwargs) -> str:
        """Combine all the templates to get the full code of the file."""
        main_template = self.environment.get_template(main_template_name)
        return main_template.render(
            **kwargs,
        )


class LaTeXFile(TemplatedFile):
    """This class represents a $\\LaTeX$ file. It generates the $\\LaTeX$ code with the
    data model and Jinja2 templates.
    """

    def __init__(
        self,
        data_model: data.RenderCVDataModel,
        environment: jinja2.Environment,
    ):
        latex_file_data_model = copy.deepcopy(data_model)

        if latex_file_data_model.cv.sections_input is not None:
            transformed_sections = transform_markdown_sections_to_latex_sections(
                latex_file_data_model.cv.sections_input
            )
            latex_file_data_model.cv.sections_input = transformed_sections

        super().__init__(latex_file_data_model, environment)

    def render_templates(self) -> tuple[str, str, list[tuple[str, list[str], str]]]:
        """Render and return all the templates for the $\\LaTeX$ file.

        Returns:
            The preamble, header, and sections of the $\\LaTeX$ file.
        """
        # Template the preamble, header, and sections:
        preamble = self.template("Preamble")
        header = self.template("Header")
        sections: list[tuple[str, list[str], str]] = []
        for section in self.cv.sections:
            section_beginning = self.template(
                "SectionBeginning",
                section_title=escape_latex_characters(section.title),
                entry_type=section.entry_type,
            )
            entries: list[str] = []
            for i, entry in enumerate(section.entries):
                is_first_entry = i == 0

                entries.append(
                    self.template(
                        section.entry_type,
                        entry=entry,
                        section_title=section.title,
                        entry_type=section.entry_type,
                        is_first_entry=is_first_entry,
                    )
                )
            section_ending = self.template(
                "SectionEnding",
                section_title=section.title,
                entry_type=section.entry_type,
            )
            sections.append((section_beginning, entries, section_ending))

        return preamble, header, sections

    def template(
        self,
        template_name: str,
        entry: Optional[data.Entry] = None,
        **kwargs,
    ) -> str:
        """Template one of the files in the `themes` directory.

        Args:
            template_name: The name of the template file.
            entry: The data model of the entry.

        Returns:
            The templated file.
        """
        result = super().template(
            self.design.theme,
            template_name,
            "tex",
            entry,
            **kwargs,
        )

        return revert_nested_latex_style_commands(result)

    def get_full_code(self) -> str:
        """Get the $\\LaTeX$ code of the file.

        Returns:
            The $\\LaTeX$ code.
        """
        preamble, header, sections = self.render_templates()
        code: str = super().get_full_code(
            "main.j2.tex",
            preamble=preamble,
            header=header,
            sections=sections,
        )
        return code

    def create_file(self, file_path: pathlib.Path):
        """Write the $\\LaTeX$ code to a file."""
        file_path.write_text(self.get_full_code(), encoding="utf-8")


class TypstFile(TemplatedFile):
    """This class represents a Typst file. It generates the Typst code with the
    data model and Jinja2 templates.
    """

    def __init__(
        self,
        data_model: data.RenderCVDataModel,
        environment: jinja2.Environment,
    ):
        typst_file_data_model = copy.deepcopy(data_model)

        if typst_file_data_model.cv.sections_input is not None:
            transformed_sections = transform_markdown_sections_to_typst_sections(
                typst_file_data_model.cv.sections_input
            )
            typst_file_data_model.cv.sections_input = transformed_sections

        super().__init__(typst_file_data_model, environment)

    def render_templates(self) -> tuple[str, str, list[tuple[str, list[str], str]]]:
        """Render and return all the templates for the $\\LaTeX$ file.

        Returns:
            The preamble, header, and sections of the $\\LaTeX$ file.
        """
        # This dictionary contains the locations of templates in the design options
        # for each entry type:
        entry_specific_templates = {
            "EducationEntry": [
                ("entry_types", "education_entry", "first_column_template"),
                ("entry_types", "education_entry", "second_column_template"),
                ("entry_types", "education_entry", "degree_column_template"),
            ],
            "ExperienceEntry": [
                ("entry_types", "experience_entry", "first_column_template"),
                ("entry_types", "experience_entry", "second_column_template"),
            ],
            "OneLineEntry": [("entry_types", "one_line_entry", "template")],
            "PublicationEntry": [
                ("entry_types", "publication_entry", "first_column_template"),
                (
                    "entry_types",
                    "publication_entry",
                    "first_column_template_without_journal",
                ),
                (
                    "entry_types",
                    "publication_entry",
                    "first_column_template_without_url",
                ),
                ("entry_types", "publication_entry", "second_column_template"),
            ],
            "NormalEntry": [
                ("entry_types", "normal_entry", "first_column_template"),
                ("entry_types", "normal_entry", "second_column_template"),
            ],
            "TextEntry": [],
            "BulletEntry": [],
        }

        # All the template field names:
        all_template_names = [
            "first_column_template",
            "first_column_template_without_url",
            "first_column_template_without_journal",
            "second_column_template",
            "template",
            "degree_column_template",
        ]

        # All the placeholders used in the templates:
        placeholder_keys = [
            "DEGREE",
            "INSTITUTION",
            "AREA",
            "SUMMARY",
            "HIGHLIGHTS",
            "POSITION",
            "COMPANY",
            "DATE",
            "LOCATION",
            "TITLE",
            "AUTHORS",
            "JOURNAL",
            "URL",
            "LABEL",
            "DETAILS",
            "NAME",
        ]

        # Template the preamble, header, and sections:
        preamble = self.template("Preamble")
        header = self.template("Header")
        sections: list[tuple[str, list[str], str]] = []
        for section in self.cv.sections:
            section_beginning = self.template(
                "SectionBeginning",
                section_title=escape_typst_characters(section.title),
                entry_type=section.entry_type,
            )

            templates = {
                location[-1]: getattr(
                    getattr(getattr(self.design, location[0], None), location[1], None),
                    location[2],
                    None,
                )
                for location in entry_specific_templates[section.entry_type]
            }

            entries: list[str] = []
            for i, entry in enumerate(section.entries):
                # Prepare placeholders:
                placeholders = {}
                for placeholder_key in placeholder_keys:
                    placeholder_value = super().template(
                        "components", placeholder_key.lower(), "typ", entry
                    )
                    placeholders[placeholder_key] = (
                        placeholder_value if placeholder_value != "None" else None
                    )

                # Substitute the placeholders in the templates:
                templates_with_substitutions = {
                    template_name: (
                        input_template_to_typst(
                            templates[template_name], placeholders  # type: ignore
                        )
                        if templates.get(template_name)
                        else None
                    )
                    for template_name in all_template_names
                }

                entries.append(
                    self.template(
                        section.entry_type,
                        entry=entry,
                        section_title=section.title,
                        entry_type=section.entry_type,
                        is_first_entry=i == 0,
                        **templates_with_substitutions,  # all the templates
                    )
                )
            section_ending = self.template(
                "SectionEnding",
                section_title=section.title,
                entry_type=section.entry_type,
            )
            sections.append((section_beginning, entries, section_ending))

        return preamble, header, sections

    def template(
        self,
        template_name: str,
        entry: Optional[data.Entry] = None,
        **kwargs,
    ) -> str:
        """Template one of the files in the `themes` directory.

        Args:
            template_name: The name of the template file.
            entry: The data model of the entry.

        Returns:
            The templated file.
        """
        return super().template(
            self.design.theme,
            template_name,
            "typ",
            entry,
            **kwargs,
        )

    def get_full_code(self) -> str:
        """Get the $\\LaTeX$ code of the file.

        Returns:
            The $\\LaTeX$ code.
        """
        preamble, header, sections = self.render_templates()
        code: str = super().get_full_code(
            "main.j2.typ",
            preamble=preamble,
            header=header,
            sections=sections,
        )
        return code

    def create_file(self, file_path: pathlib.Path):
        """Write the $\\LaTeX$ code to a file."""
        file_path.write_text(self.get_full_code(), encoding="utf-8")


class MarkdownFile(TemplatedFile):
    """This class represents a Markdown file. It generates the Markdown code with the
    data model and Jinja2 templates. Markdown files are generated to produce an HTML
    which can be copy-pasted to [Grammarly](https://app.grammarly.com/) for
    proofreading.
    """

    def render_templates(self) -> tuple[str, list[tuple[str, list[str]]]]:
        """Render and return all the templates for the Markdown file.

        Returns:
            The header and sections of the Markdown file.
        """
        # Template the header and sections:
        header = self.template("Header")
        sections: list[tuple[str, list[str]]] = []
        for section in self.cv.sections:
            section_beginning = self.template(
                "SectionBeginning",
                section_title=section.title,
                entry_type=section.entry_type,
            )
            entries: list[str] = []
            for i, entry in enumerate(section.entries):
                is_first_entry = bool(i == 0)
                entries.append(
                    self.template(
                        section.entry_type,
                        entry=entry,
                        section_title=section.title,
                        entry_type=section.entry_type,
                        is_first_entry=is_first_entry,
                    )
                )
            sections.append((section_beginning, entries))

        result: tuple[str, list[tuple[str, list[str]]]] = (header, sections)
        return result

    def template(
        self,
        template_name: str,
        entry: Optional[data.Entry] = None,
        **kwargs,
    ) -> str:
        """Template one of the files in the `themes` directory.

        Args:
            template_name: The name of the template file.
            entry: The data model of the entry.

        Returns:
            The templated file.
        """
        return super().template(
            "markdown",
            template_name,
            "md",
            entry,
            **kwargs,
        )

    def get_full_code(self) -> str:
        """Get the Markdown code of the file.

        Returns:
            The Markdown code.
        """
        header, sections = self.render_templates()
        code: str = super().get_full_code(
            "main.j2.md",
            header=header,
            sections=sections,
        )
        return code

    def create_file(self, file_path: pathlib.Path):
        """Write the Markdown code to a file."""
        file_path.write_text(self.get_full_code(), encoding="utf-8")


def input_template_to_typst(
    input_template: str, placeholders: dict[str, Optional[str]]
) -> str:
    """Convert an input template to Typst.

    Args:
        input_template: The input template.
        placeholders: The placeholders and their values.

    Returns:
        Typst string.
    """
    output = replace_placeholders_with_actual_values(
        markdown_to_typst(input_template), placeholders
    )

    # Check if there are any letters in the input template. If not, return an empty
    if not re.search(r"[a-zA-Z]", input_template):
        return ""

    # Finsh italic and bold links and fix them:
    # For example:
    # Convert `#[_#link("https://google.com")[italic link]]`` to
    # `#link("https://google.com")[_italic link_]`
    output = re.sub(
        r"#\[_#link\(\"(.*?)\"\)\[(.*?)\]_\]",
        r'#link("\1")[_\2_]',
        output,
    )
    output = re.sub(
        r"#\[\*#link\(\"(.*?)\"\)\[(.*?)\]\*\]",
        r'#link("\1")[*\2*]',
        output,
    )
    output = re.sub(
        r"#\[\*_#link\(\"(.*?)\"\)\[(.*?)\]_\*\]",
        r'#link("\1")[*_\2_*]',
        output,
    )

    # Replace all multiple \n with a single \n:
    output = re.sub(r"\n+", r"\n\n", output)

    # Make all \n s, \n\n:
    return output


def revert_nested_latex_style_commands(latex_string: str) -> str:
    """Revert the nested $\\LaTeX$ style commands to allow users to unbold or
    unitalicize a bold or italicized text.

    Args:
        latex_string: The string to revert the nested $\\LaTeX$ style commands.

    Returns:
        The string with the reverted nested $\\LaTeX$ style commands.
    """
    # If there is nested \textbf, \textit, or \underline commands, replace the inner
    # ones with \textnormal:
    nested_commands_to_look_for = [
        "textbf",
        "textit",
        "underline",
    ]

    for command in nested_commands_to_look_for:
        nested_commands = True
        while nested_commands:
            # replace all the inner commands with \textnormal until there are no
            # nested commands left:

            # find the first nested command:
            nested_commands = re.findall(
                rf"\\{command}{{[^}}]*?(\\{command}{{.*?}})", latex_string
            )

            # replace the nested command with \textnormal:
            for nested_command in nested_commands:
                new_command = nested_command.replace(command, "textnormal")
                latex_string = latex_string.replace(nested_command, new_command)

    return latex_string


def escape_characters(string: str, escape_dictionary: dict[str, str]) -> str:
    """Escape characters in a string by using `escape_dictionary`, where keys are
    characters to escape and values are their escaped versions.

    Example:
        ```python
        escape_characters("This is a # string.", {"#": "\\#"})
        ```
        returns
        `"This is a \\# string."`

    Args:
        string: The string to escape.
        escape_dictionary: The dictionary of escape characters.

    Returns:
        The escaped string.
    """

    translation_map = str.maketrans(escape_dictionary)

    # Don't escape urls as hyperref package will do it automatically:
    # Find all the links in the sentence:
    links = re.findall(r"\[(.*?)\]\((.*?)\)", string)

    # Replace the links with a dummy string and save links with escaped characters:
    new_links = []
    for i, link in enumerate(links):
        placeholder = link[0]
        escaped_placeholder = placeholder.translate(translation_map)
        url = link[1]

        original_link = f"[{placeholder}]({url})"
        string = string.replace(original_link, f"!!-link{i}-!!")

        new_link = f"[{escaped_placeholder}]({url})"
        new_links.append(new_link)

    # If there are equations in the sentence, don't escape the special characters:
    # Find all the equations in the sentence:
    equations = re.findall(r"(\$\$.*?\$\$)", string)
    new_equations = []
    for i, equation in enumerate(equations):
        string = string.replace(equation, f"!!-equation{i}-!!")

        # Keep only one dollar sign for inline equations:
        new_equation = equation.replace("$$", "$")
        new_equations.append(new_equation)

    # Don't touch latex commands:
    # Find all the latex commands in the sentence:
    latex_commands = re.findall(r"\\[a-zA-Z]+\{.*?\}", string)
    for i, latex_command in enumerate(latex_commands):
        string = string.replace(latex_command, f"!!-latex{i}-!!")

    # Loop through the letters of the sentence and if you find an escape character,
    # replace it with its LaTeX equivalent:
    string = string.translate(translation_map)

    # Replace !!-link{i}-!!" with the original urls:
    for i, new_link in enumerate(new_links):
        string = string.replace(f"!!-link{i}-!!", new_link)

    # Replace !!-equation{i}-!!" with the original equations:
    for i, new_equation in enumerate(new_equations):
        string = string.replace(f"!!-equation{i}-!!", new_equation)

    # Replace !!-latex{i}-!!" with the original latex commands:
    for i, latex_command in enumerate(latex_commands):
        string = string.replace(f"!!-latex{i}-!!", latex_command)

    return string


def escape_typst_characters(string: str) -> str:
    """Escape Typst characters in a string by adding a backslash before them.

    Example:
        ```python
        escape_typst_characters("This is a # string.")
        ```
        returns
        `"This is a \\# string."`

    Args:
        string: The string to escape.

    Returns:
        The escaped string.
    """
    escape_dictionary = {
        "[": "\\[",
        "]": "\\]",
        "(": "\\(",
        ")": "\\)",
        "\\": "\\\\",
        '"': '\\"',
        "#": "\\#",
        "$": "\\$",
        "@": "\\@",
    }

    return escape_characters(string, escape_dictionary)


def escape_latex_characters(string: str) -> str:
    """Escape $\\LaTeX$ characters in a string by adding a backslash before them.

    Example:
        ```python
        escape_latex_characters("This is a # string.")
        ```
        returns
        `"This is a \\# string."`

    Args:
        string: The string to escape.

    Returns:
        The escaped string.
    """

    # Dictionary of escape characters:
    escape_dictionary = {
        "{": "\\{",
        "}": "\\}",
        # "\\": "\\textbackslash{}",
        "#": "\\#",
        "%": "\\%",
        "&": "\\&",
        "~": "\\textasciitilde{}",
        "$": "\\$",
        "_": "\\_",
        "^": "\\textasciicircum{}",
    }

    return escape_characters(string, escape_dictionary)


def markdown_to_typst(markdown_string: str) -> str:
    """Convert a Markdown string to Typst.

    Example:
        ```python
        markdown_to_typst(
            "This is a **bold** text with an [*italic link*](https://google.com)."
        )
        ```

        returns

        `"This is a *bold* text with an #link("https://google.com")[_italic link_]."`

    Args:
        markdown_string: The Markdown string to convert.

    Returns:
        The Typst string.
    """
    # convert links
    links = re.findall(r"\[([^\]\[]*)\]\((.*?)\)", markdown_string)
    if links is not None:
        for link in links:
            link_text = link[0]
            link_url = link[1]

            old_link_string = f"[{link_text}]({link_url})"
            new_link_string = f'#link("{link_url}")[{link_text}]'

            markdown_string = markdown_string.replace(old_link_string, new_link_string)

    # convert bold and italic:
    bold_and_italics = re.findall(r"\*\*\*(.+?)\*\*\*", markdown_string)
    if bold_and_italics is not None:
        for bold_and_italic_text in bold_and_italics:
            old_bold_and_italic_text = f"***{bold_and_italic_text}***"
            new_bold_and_italic_text = f"#[ONE_STAR_{bold_and_italic_text}_ONE_STAR]"

            markdown_string = markdown_string.replace(
                old_bold_and_italic_text, new_bold_and_italic_text
            )

    # convert bold
    bolds = re.findall(r"\*\*(.+?)\*\*", markdown_string)
    if bolds is not None:
        for bold_text in bolds:
            old_bold_text = f"**{bold_text}**"
            new_bold_text = f"#[ONE_STAR{bold_text}ONE_STAR]"
            markdown_string = markdown_string.replace(old_bold_text, new_bold_text)

    # convert italic
    italics = re.findall(r"\*(.+?)\*", markdown_string)
    if italics is not None:
        for italic_text in italics:
            old_italic_text = f"*{italic_text}*"
            new_italic_text = f"#[_{italic_text}_]"

            markdown_string = markdown_string.replace(old_italic_text, new_italic_text)

    return markdown_string.replace("ONE_STAR", "*")


def markdown_to_latex(markdown_string: str) -> str:
    """Convert a Markdown string to $\\LaTeX$.

    This function is called during the reading of the input file. Before the validation
    process, each input field is converted from Markdown to $\\LaTeX$.

    Example:
        ```python
        markdown_to_latex(
            "This is a **bold** text with an [*italic link*](https://google.com)."
        )
        ```

        returns

        `"This is a \\textbf{bold} text with a \\href{https://google.com}{\\textit{link}}."`

    Args:
        markdown_string: The Markdown string to convert.

    Returns:
        The $\\LaTeX$ string.
    """
    # convert links
    links = re.findall(r"\[([^\]\[]*)\]\((.*?)\)", markdown_string)
    if links is not None:
        for link in links:
            link_text = link[0]
            link_url = link[1]

            old_link_string = f"[{link_text}]({link_url})"
            new_link_string = "\\href{" + link_url + "}{" + link_text + "}"

            markdown_string = markdown_string.replace(old_link_string, new_link_string)

    # convert bold
    bolds = re.findall(r"\*\*(.+?)\*\*", markdown_string)
    if bolds is not None:
        for bold_text in bolds:
            old_bold_text = f"**{bold_text}**"
            new_bold_text = "\\textbf{" + bold_text + "}"

            markdown_string = markdown_string.replace(old_bold_text, new_bold_text)

    # convert italic
    italics = re.findall(r"\*(.+?)\*", markdown_string)
    if italics is not None:
        for italic_text in italics:
            old_italic_text = f"*{italic_text}*"
            new_italic_text = "\\textit{" + italic_text + "}"

            markdown_string = markdown_string.replace(old_italic_text, new_italic_text)

    return markdown_string


def transform_markdown_sections_to_something_else_sections(
    sections: dict[str, data.SectionContents],
    functions_to_apply: list[Callable],
) -> Optional[dict[str, data.SectionContents]]:
    """
    Recursively loop through sections and update all the strings by applying the
    `functions_to_apply` functions, given as an argument.

    Args:
        sections: Sections with Markdown strings.
        functions_to_apply: Functions to apply to the strings.

    Returns:
        Sections with updated strings.
    """

    def apply_functions_to_string(string: str):
        for function in functions_to_apply:
            string = function(string)
        return string

    for key, value in sections.items():
        # loop through the list and apply markdown_to_latex and escape_latex_characters
        # to each item:
        transformed_list = []
        for entry in value:
            if isinstance(entry, str):
                # Then it means it's a TextEntry.
                result = apply_functions_to_string(entry)
                transformed_list.append(result)
            else:
                # Then it means it's one of the other entries.
                fields_to_skip = ["doi"]
                entry_as_dict = entry.model_dump()
                for entry_key, inner_value in entry_as_dict.items():
                    if entry_key in fields_to_skip:
                        continue
                    if isinstance(inner_value, str):
                        result = apply_functions_to_string(inner_value)
                        setattr(entry, entry_key, result)
                    elif isinstance(inner_value, list):
                        for j, item in enumerate(inner_value):
                            if isinstance(item, str):
                                inner_value[j] = apply_functions_to_string(item)
                        setattr(entry, entry_key, inner_value)
                transformed_list.append(entry)

        sections[key] = transformed_list

    return sections


def transform_markdown_sections_to_latex_sections(
    sections: dict[str, data.SectionContents],
) -> Optional[dict[str, data.SectionContents]]:
    """
    Recursively loop through sections and convert all the Markdown strings (user input
    is in Markdown format) to $\\LaTeX$ strings. Also, escape special $\\LaTeX$
    characters.

    Args:
        sections: Sections with Markdown strings.

    Returns:
        Sections with $\\LaTeX$ strings.
    """
    return transform_markdown_sections_to_something_else_sections(
        sections,
        [escape_latex_characters, markdown_to_latex],
    )


def transform_markdown_sections_to_typst_sections(
    sections: dict[str, data.SectionContents],
) -> Optional[dict[str, data.SectionContents]]:
    """
    Recursively loop through sections and convert all the Markdown strings (user input
    is in Markdown format) to Typst strings.

    Args:
        sections: Sections with Markdown strings.

    Returns:
        Sections with Typst strings.
    """
    return transform_markdown_sections_to_something_else_sections(
        sections,
        [escape_typst_characters, markdown_to_typst],
    )


def replace_placeholders_with_actual_values(
    text: str, placeholders: dict[str, Optional[str]]
) -> str:
    """Replace the placeholders in a string with actual values.

    This function can be used as a Jinja2 filter in templates.

    Args:
        text: The text with placeholders.
        placeholders: The placeholders and their values.

    Returns:
        The string with actual values.
    """
    for placeholder, value in placeholders.items():
        if value:
            text = text.replace(placeholder, str(value))
        else:
            # Replace the placeholder and the characters around it with an empty string:
            text = re.sub(rf"[^\s]*{placeholder}[^\s]*", "", text)

    return text


def make_matched_part_something(
    value: str,
    something: Literal["textbf", "underline", "textit", "mbox"],
    match_str: Optional[str] = None,
) -> str:
    """Make the matched parts of the string something. If the match_str is None, the
    whole string will be made something.

    Warning:
        This function shouldn't be used directly. Use `make_matched_part_bold`,
        `make_matched_part_underlined`, `make_matched_part_italic`, or
        `make_matched_part_non_line_breakable instead.
    Args:
        value: The string to make something.
        something: The $\\LaTeX$ command to use.
        match_str: The string to match.

    Returns:
        The string with the matched part something.
    """
    if match_str is None:
        # If the match_str is None, the whole string will be made something:
        value = f"\\{something}{{{value}}}"
    elif match_str in value and match_str != "":
        # If the match_str is in the value, then make the matched part something:
        value = value.replace(match_str, f"\\{something}{{{match_str}}}")

    return value


def make_matched_part_bold(value: str, match_str: Optional[str] = None) -> str:
    """Make the matched parts of the string bold. If the match_str is None, the whole
    string will be made bold.

    This function can be used as a Jinja2 filter in templates.

    Example:
        ```python
        make_it_bold("Hello World!", "Hello")
        ```

        returns

        `"\\textbf{Hello} World!"`

    Args:
        value: The string to make bold.
        match_str: The string to match.

    Returns:
        The string with the matched part bold.
    """
    return make_matched_part_something(value, "textbf", match_str)


def make_matched_part_underlined(value: str, match_str: Optional[str] = None) -> str:
    """Make the matched parts of the string underlined. If the match_str is None, the
    whole string will be made underlined.

    This function can be used as a Jinja2 filter in templates.

    Example:
        ```python
        make_it_underlined("Hello World!", "Hello")
        ```

        returns

        `"\\underline{Hello} World!"`

    Args:
        value: The string to make underlined.
        match_str: The string to match.

    Returns:
        The string with the matched part underlined.
    """
    return make_matched_part_something(value, "underline", match_str)


def make_matched_part_italic(value: str, match_str: Optional[str] = None) -> str:
    """Make the matched parts of the string italic. If the match_str is None, the whole
    string will be made italic.

    This function can be used as a Jinja2 filter in templates.

    Example:
        ```python
        make_it_italic("Hello World!", "Hello")
        ```

        returns

        `"\\textit{Hello} World!"`

    Args:
        value: The string to make italic.
        match_str: The string to match.

    Returns:
        The string with the matched part italic.
    """
    return make_matched_part_something(value, "textit", match_str)


def make_matched_part_non_line_breakable(
    value: str, match_str: Optional[str] = None
) -> str:
    """Make the matched parts of the string non line breakable. If the match_str is
    None, the whole string will be made nonbreakable.

    This function can be used as a Jinja2 filter in templates.

    Example:
        ```python
        make_it_nolinebreak("Hello World!", "Hello")
        ```

        returns

        `"\\mbox{Hello} World!"`

    Args:
        value: The string to disable line breaks.
        match_str: The string to match.

    Returns:
        The string with the matched part non line breakable.
    """
    return make_matched_part_something(value, "mbox", match_str)


def abbreviate_name(name: Optional[str]) -> str:
    """Abbreviate a name by keeping the first letters of the first names.

    This function can be used as a Jinja2 filter in templates.

    Example:
        ```python
        abbreviate_name("John Doe")
        ```

        returns

        `"J. Doe"`

    Args:
        name: The name to abbreviate.

    Returns:
        The abbreviated name.
    """
    if name is None:
        return ""

    number_of_words = len(name.split(" "))

    if number_of_words == 1:
        return name

    first_names = name.split(" ")[:-1]
    first_names_initials = [first_name[0] + "." for first_name in first_names]
    last_name = name.split(" ")[-1]

    return " ".join(first_names_initials) + " " + last_name


def divide_length_by(length: str, divider: float) -> str:
    r"""Divide a length by a number. Length is a string with the following regex
    pattern: `\d+\.?\d* *(cm|in|pt|mm|ex|em)`

    This function can be used as a Jinja2 filter in templates.

    Example:
        ```python
        divide_length_by("10.4cm", 2)
        ```

        returns

        `"5.2cm"`

    Args:
        length: The length to divide.
        divider: The number to divide the length by.

    Returns:
        The divided length.
    """
    # Get the value as a float and the unit as a string:
    value = re.search(r"\d+\.?\d*", length)

    if value is None:
        message = f"Invalid length {length}!"
        raise ValueError(message)

    value = value.group()

    if divider <= 0:
        message = f"The divider must be greater than 0, but got {divider}!"
        raise ValueError(message)

    unit = re.findall(r"[^\d\.\s]+", length)[0]

    return str(float(value) / divider) + " " + unit


def get_an_item_with_a_specific_attribute_value(
    items: Optional[list[Any]], attribute: str, value: Any
) -> Any:
    """Get an item from a list of items with a specific attribute value.

    Example:
        ```python
        get_an_item_with_a_specific_attribute_value(
            [item1, item2],  # where item1.name = "John" and item2.name = "Jane"
            "name",
            "Jane",
        )
        ```
        returns
        `item2`

    This function can be used as a Jinja2 filter in templates.

    Args:
        items: The list of items.
        attribute: The attribute to check.
        value: The value of the attribute.

    Returns:
        The item with the specific attribute value.
    """
    if items is not None:
        for item in items:
            if not hasattr(item, attribute):
                message = f"The attribute {attribute} doesn't exist in the item {item}!"
                raise AttributeError(message)

            if getattr(item, attribute) == value:
                return item

    return None


# Only one Jinja2 environment is needed for all the templates:
jinja2_environment: Optional[jinja2.Environment] = None


def setup_jinja2_environment() -> jinja2.Environment:
    """Setup and return the Jinja2 environment for templating the $\\LaTeX$ files.

    Returns:
        The theme environment.
    """
    global jinja2_environment  # noqa: PLW0603
    themes_directory = pathlib.Path(__file__).parent.parent / "themes"

    if jinja2_environment is None:
        # create a Jinja2 environment:
        # we need to add the current working directory because custom themes might be used.
        environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader([pathlib.Path.cwd(), themes_directory]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # set custom delimiters for LaTeX templating:
        environment.block_start_string = "((*"
        environment.block_end_string = "*))"
        environment.variable_start_string = "<<"
        environment.variable_end_string = ">>"
        environment.comment_start_string = "((#"
        environment.comment_end_string = "#))"

        # add custom filters to make it easier to template the LaTeX files and add new
        # themes:
        environment.filters["make_it_bold"] = make_matched_part_bold
        environment.filters["make_it_underlined"] = make_matched_part_underlined
        environment.filters["make_it_italic"] = make_matched_part_italic
        environment.filters["make_it_nolinebreak"] = (
            make_matched_part_non_line_breakable
        )
        environment.filters["make_it_something"] = make_matched_part_something
        environment.filters["divide_length_by"] = divide_length_by
        environment.filters["abbreviate_name"] = abbreviate_name
        environment.filters["replace_placeholders_with_actual_values"] = (
            replace_placeholders_with_actual_values
        )
        environment.filters["get_an_item_with_a_specific_attribute_value"] = (
            get_an_item_with_a_specific_attribute_value
        )
        environment.filters["escape_latex_characters"] = escape_latex_characters
        environment.filters["escape_typst_characters"] = escape_typst_characters
        environment.filters["markdown_to_latex"] = markdown_to_latex
        environment.filters["markdown_to_typst"] = markdown_to_typst

        jinja2_environment = environment
    else:
        # update the loader in case the current working directory has changed:
        jinja2_environment.loader = jinja2.FileSystemLoader(
            [
                pathlib.Path.cwd(),
                themes_directory,
            ]
        )

    return jinja2_environment
