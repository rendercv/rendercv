"""
The `rendercv.renderer.templater` module contains all the necessary classes and
functions for templating the Typst and Markdown files from the `RenderCVDataModel`
object.
"""

import copy
import pathlib
import re
from collections.abc import Callable
from typing import overload, get_origin, get_args

import jinja2
import pydantic

from .. import data


class TemplatedFile:
    """This class is a base class for `TypstFile`, and `MarkdownFile` classes. It
    contains the common methods and attributes for both classes. These classes are used
    to generate the Typst and Markdown files with the data model and Jinja2
    templates.

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
        self.locale = data_model.locale
        self.environment = environment

    def template(
        self,
        theme_name: str,
        template_name: str,
        extension: str,
        entry: data.Entry | None = None,
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
            # Iterate over the model fields themselves (not the serialised dict) so
            # we *never* coerce complex objects like `HttpUrl` into plain strings.
            for key, model_field in entry.__class__.model_fields.items():
                if key in fields_to_ignore:
                    continue

                value = getattr(entry, key)
                if value is not None:
                    continue

                field_type = model_field.annotation
                origin = get_origin(field_type)

                # 1) Identify list-like annotations (e.g., list[str] | None)
                is_list_field = (
                    origin is list
                    or field_type is list
                    or any(get_origin(arg) is list or arg is list for arg in get_args(field_type))
                )

                # 2) Identify *plain* string annotations (str | None)
                is_string_field = (
                    field_type is str
                    or (
                        origin is not None
                        and all(arg in {str, type(None)} for arg in get_args(field_type))
                        and any(arg is str for arg in get_args(field_type))
                    )
                )

                if is_list_field:
                    entry.__setattr__(key, [])
                elif is_string_field:
                    entry.__setattr__(key, "")

        # The arguments of the template can be used in the template file:
        return template.render(
            cv=self.cv,
            design=self.design,
            locale=self.locale,
            entry=entry,
            today=data.format_date(data.get_date_input()),
            **kwargs,
        )

    def get_full_code(self, main_template_name: str, **kwargs) -> str:
        """Combine all the templates to get the full code of the file."""
        main_template = self.environment.get_template(main_template_name)
        return main_template.render(
            **kwargs,
        )


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

    def render_templates(
        self,
    ) -> tuple[str, str, list[tuple[str, list[str], str, str]]]:
        """Render and return all the templates for the Typst file.

        Returns:
            The preamble, header, and sections of the Typst file.
        """
        # All the template field names:
        all_template_names = [
            "main_column_first_row_template",
            "main_column_second_row_template",
            "main_column_second_row_without_url_template",
            "main_column_second_row_without_journal_template",
            "date_and_location_column_template",
            "template",
            "degree_column_template",
        ]

        # All the placeholders used in the templates:
        sections_input: dict[str, list[pydantic.BaseModel]] = self.cv.sections_input  # type: ignore
        # Loop through the sections and entries to find all the field names:
        placeholder_keys: set[str] = set()
        if sections_input:
            for section in sections_input.values():
                for entry in section:
                    if isinstance(entry, str):
                        break
                    entry_dictionary = entry.model_dump()
                    for key in entry_dictionary:
                        placeholder_keys.add(key.upper())

        pattern = re.compile(r"(?<!^)(?=[A-Z])")

        def camel_to_snake(name: str) -> str:
            return pattern.sub("_", name).lower()

        # Template the preamble, header, and sections:
        preamble = self.template("Preamble")
        header = self.template("Header")
        sections: list[tuple[str, list[str], str, str]] = []
        for section in self.cv.sections:
            section_beginning = self.template(
                "SectionBeginning",
                section_title=escape_typst_characters(section.title),
                entry_type=section.entry_type,
            )

            templates = {
                template_name: getattr(
                    getattr(
                        getattr(self.design, "entry_types", None),
                        camel_to_snake(section.entry_type),
                        None,
                    ),
                    template_name,
                    None,
                )
                for template_name in all_template_names
            }

            entries: list[str] = []
            for i, entry in enumerate(section.entries):
                # Prepare placeholders:
                placeholders = {}
                for placeholder_key in placeholder_keys:
                    components_path = (
                        pathlib.Path(__file__).parent.parent / "themes" / "components"
                    )
                    lowercase_placeholder_key = placeholder_key.lower()
                    if (
                        components_path / f"{lowercase_placeholder_key}.j2.typ"
                    ).exists():
                        placeholder_value = super().template(
                            "components",
                            lowercase_placeholder_key,
                            "typ",
                            entry,
                            section_title=section.title,
                        )
                    else:
                        placeholder_value = getattr(entry, placeholder_key, None)

                    placeholders[placeholder_key] = (
                        placeholder_value if placeholder_value != "None" else None
                    )

                # Substitute the placeholders in the templates:
                templates_with_substitutions = {
                    template_name: (
                        input_template_to_typst(
                            templates[template_name],
                            placeholders,  # type: ignore
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
            sections.append(
                (section_beginning, entries, section_ending, section.entry_type)
            )

        return preamble, header, sections

    def template(
        self,
        template_name: str,
        entry: data.Entry | None = None,
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
        """Get the Typst code of the file.

        Returns:
            The Typst code.
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
        """Write the Typst code to a file."""
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
        entry: data.Entry | None = None,
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
    input_template: str | None, placeholders: dict[str, str | None]
) -> str:
    """Convert an input template to Typst.

    Args:
        input_template: The input template.
        placeholders: The placeholders and their values.

    Returns:
        Typst string.
    """
    if input_template is None:
        return ""

    output = replace_placeholders_with_actual_values(
        markdown_to_typst(input_template),
        placeholders,
    )

    # If \n is escaped, revert:
    output = output.replace("\\n", "\n")

    # If there are blank italics and bolds, remove them:
    output = output.replace("#emph[]", "")
    output = output.replace("#strong[]", "")

    # Check if there are any letters in the input template. If not, return an empty
    if not re.search(r"[a-zA-Z]", input_template):
        return ""

    # Find italic and bold links and fix them:
    # For example:
    # Convert `#emph[#link("https://google.com")[italic link]]` to
    # `#link("https://google.com")[#emph[italic link]]`
    output = re.sub(
        r"#emph\[#link\(\"(.*?)\"\)\[(.*?)\]\]",
        r'#link("\1")[#emph[\2]]',
        output,
    )
    output = re.sub(
        r"#strong\[#link\(\"(.*?)\"\)\[(.*?)\]\]",
        r'#link("\1")[#strong[\2]]',
        output,
    )
    output = re.sub(
        r"#strong\[#emph\[#link\(\"(.*?)\"\)\[(.*?)\]\]\]",
        r'#link("\1")[#strong[#emph[\2]]]',
        output,
    )

    # Replace all multiple \n with a double \n:
    output = re.sub(r"\n+", r"\n\n", output)

    # Strip whitespace
    output = output.strip()

    # Strip non-alphanumeric, non-typst characters from the beginning and end of the
    # string. For example, when location is not given in a template like this:
    # "NAME -- LOCATION", "NAME -- " should become "NAME".
    output = re.sub(r"^[^\w\s#\[\]\n\(\)]*", "", output)
    output = re.sub(r"[^\w\s#\[\]\n\(\)]*$", "", output)

    return output  # noqa: RET504


@overload
def remove_typst_commands(string: None) -> None: ...


@overload
def remove_typst_commands(string: str) -> str: ...


def remove_typst_commands(string: str | None) -> str | None:
    """Remove Typst commands from a string.

    Args:
        string: The string to remove Typst commands from.

    Returns:
        The string without Typst commands.
    """
    if string:
        commands = re.findall(r"\#.*?\[.*?\]", string)
        for command in commands:
            string = string.replace(command, "")

        return string

    return None


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

    # If there are Typst commands, don't escape the special characters:
    commands = re.findall(r"(\#.*?\[.*?\])", string)
    for i, command in enumerate(commands):
        string = string.replace(command, f"!!-command{i}-!!")

    # Loop through the letters of the sentence and if you find an escape character,
    # replace it with their equivalent:
    string = string.translate(translation_map)

    # Replace !!-link{i}-!!" with the original urls:
    for i, new_link in enumerate(new_links):
        string = string.replace(f"!!-link{i}-!!", new_link)

    # Replace !!-equation{i}-!!" with the original equations:
    for i, new_equation in enumerate(new_equations):
        string = string.replace(f"!!-equation{i}-!!", new_equation)

    # Replace !!-command{i}-!!" with the original commands:
    for i, command in enumerate(commands):
        string = string.replace(f"!!-command{i}-!!", command)

    return string


@overload
def escape_typst_characters(string: None) -> None: ...


@overload
def escape_typst_characters(string: str) -> str: ...


def escape_typst_characters(string: str | None) -> str | None:
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
    if string is None:
        return None

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
        "%": "\\%",
        "~": "\\~",
        "_": "\\_",
        "/": "\\/",
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

    # Process escaped asterisks in the yaml (such that they are actual asterisks,
    # and not markers for bold/italics). We need to temporarily replace them with
    # a dummy string.

    ONE_STAR = "ONE_STAR"

    # NOTE: We get a mix of escape levels depending on whether the star is in a quoted
    #       or unquoted yaml entry. This is a bit of a mess but below seems to work
    #       as i would instinctively expect.
    markdown_string = markdown_string.replace("\\\\*", ONE_STAR)
    markdown_string = markdown_string.replace("\\*", ONE_STAR)

    # convert bold and italic:
    bold_and_italics = re.findall(r"\*\*\*(.+?)\*\*\*", markdown_string)
    if bold_and_italics is not None:
        for bold_and_italic_text in bold_and_italics:
            old_bold_and_italic_text = f"***{bold_and_italic_text}***"
            new_bold_and_italic_text = f"#strong[#emph[{bold_and_italic_text}]]"

            markdown_string = markdown_string.replace(
                old_bold_and_italic_text, new_bold_and_italic_text
            )

    # convert bold
    bolds = re.findall(r"\*\*(.+?)\*\*", markdown_string)
    if bolds is not None:
        for bold_text in bolds:
            old_bold_text = f"**{bold_text}**"
            new_bold_text = f"#strong[{bold_text}]"
            markdown_string = markdown_string.replace(old_bold_text, new_bold_text)

    # convert italic
    italics = re.findall(r"\*(.+?)\*", markdown_string)
    if italics is not None:
        for italic_text in italics:
            old_italic_text = f"*{italic_text}*"
            new_italic_text = f"#emph[{italic_text}]"

            markdown_string = markdown_string.replace(old_italic_text, new_italic_text)

    # Revert normal asterisks then convert them to Typst's asterisks
    markdown_string = markdown_string.replace(ONE_STAR, "*")

    # convert any remaining asterisks to Typst's asterisk
    # - Asterisk with a space can just be replaced.
    # - Asterisk without a space needs a zero-width box to delimit it.
    typst_asterisk = "#sym.ast.basic"
    zero_box = "#h(0pt, weak: true) "
    markdown_string = markdown_string.replace("* ", typst_asterisk + " ")
    markdown_string = markdown_string.replace("*", typst_asterisk + zero_box)

    # At this point, the document ought to have absolutely no '*' characters left!
    # NOTE: The final typst file might still have some asterisks when specifying a
    #       size, for example `#v(design-text-font-size * 0.4)`
    # XXX: Maybe put this behind some kind of debug flag? -MK
    # assert "*" not in markdown_string

    return markdown_string  # noqa: RET504


def transform_markdown_sections_to_something_else_sections(
    sections: dict[str, data.SectionContents],
    functions_to_apply: list[Callable],
) -> dict[str, data.SectionContents] | None:
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
        transformed_list = []
        for entry in value:
            if isinstance(entry, str):
                # Then it means it's a TextEntry.
                result = apply_functions_to_string(entry)
                transformed_list.append(result)
            else:
                # Then it means it's one of the other entries.
                # Fields whose *value* should never be string-processed / overwritten
                # because they are stored as specialised objects (e.g. pydantic HttpUrl).
                fields_to_skip = {"doi", "url", "website"}

                for entry_key, model_field in entry.__class__.model_fields.items():
                    if entry_key in fields_to_skip:
                        continue

                    inner_value = getattr(entry, entry_key)

                    # Process str
                    if isinstance(inner_value, str):
                        setattr(entry, entry_key, apply_functions_to_string(inner_value))

                    # Process list[str]
                    elif isinstance(inner_value, list):
                        new_list: list = []
                        changed = False
                        for item in inner_value:
                            if isinstance(item, str):
                                new_list.append(apply_functions_to_string(item))
                                changed = True
                            else:
                                new_list.append(item)
                        if changed:
                            setattr(entry, entry_key, new_list)
                transformed_list.append(entry)

        sections[key] = transformed_list

    return sections


def transform_markdown_sections_to_typst_sections(
    sections: dict[str, data.SectionContents],
) -> dict[str, data.SectionContents] | None:
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
    text: str,
    placeholders: dict[str, str | None],
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
            text = text.replace(placeholder, "")

    return text


class Jinja2Environment:
    instance: "Jinja2Environment"
    environment: jinja2.Environment
    current_working_directory: pathlib.Path | None = None

    def __new__(cls):
        if (
            not hasattr(cls, "instance")
            or cls.current_working_directory != pathlib.Path.cwd()
        ):
            cls.instance = super().__new__(cls)

            themes_directory = pathlib.Path(__file__).parent.parent / "themes"

            # create a Jinja2 environment:
            # we need to add the current working directory because custom themes might be used.
            environment = jinja2.Environment(
                loader=jinja2.FileSystemLoader([pathlib.Path.cwd(), themes_directory]),
                trim_blocks=True,
                lstrip_blocks=True,
            )

            # set custom delimiters:
            environment.block_start_string = "((*"
            environment.block_end_string = "*))"
            environment.variable_start_string = "<<"
            environment.variable_end_string = ">>"
            environment.comment_start_string = "((#"
            environment.comment_end_string = "#))"

            # add custom Jinja2 filters:
            environment.filters["replace_placeholders_with_actual_values"] = (
                replace_placeholders_with_actual_values
            )
            environment.filters["escape_typst_characters"] = escape_typst_characters
            environment.filters["markdown_to_typst"] = markdown_to_typst
            environment.filters["make_a_url_clean"] = data.make_a_url_clean
            environment.filters["remove_typst_commands"] = remove_typst_commands

            cls.environment = environment

        return cls.instance
