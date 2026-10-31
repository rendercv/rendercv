"""Render the documentation's entry examples directly to PNG with Typst."""

import pathlib
import tempfile

from rendercv.renderer.pdf_png import get_typst_compiler
from rendercv.renderer.templater.model_processor import process_model
from rendercv.renderer.templater.templater import render_section, render_single_template
from rendercv.schema.models.design.built_in_design import available_themes
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.yaml_reader import read_yaml

repository_root = pathlib.Path(__file__).parent.parent


def render_entry_figure(model: RenderCVModel, root: pathlib.Path) -> bytes:
    """Render one section on a page whose height follows its content.

    Args:
        model: CV containing the example section and its theme.
        root: Working directory for the compiler.

    Returns:
        The PNG image.
    """
    processed = process_model(model, "typst")
    preamble = render_single_template(
        "typst", "Preamble.j2.typ", processed, page_height="auto"
    )
    section = render_section(processed, "typst", processed.cv.rendercv_sections[0])
    source = f"{preamble}\n{section}"
    compiler = get_typst_compiler(None, root)
    images = compiler.compile(source.encode(), format="png", ppi=300)
    if isinstance(images, list):
        (image,) = images
    else:
        image = images
    assert isinstance(image, bytes)
    return image


def main() -> None:
    """Update every theme's figures from the documentation's sample entries."""
    entries = read_yaml(repository_root / "docs" / "user_guide" / "sample_entries.yaml")
    image_directory = repository_root / "docs" / "assets" / "images"
    with tempfile.TemporaryDirectory(prefix="rendercv-figures-") as temporary:
        for theme in available_themes:
            directory = image_directory / theme
            directory.mkdir(parents=True, exist_ok=True)
            for entry_type, entry in entries.items():
                model = RenderCVModel.model_validate(
                    {
                        "cv": {"sections": {entry_type: [entry]}},
                        "design": {
                            "theme": theme,
                            "page": {
                                "show_footer": False,
                                "show_top_note": False,
                                "top_margin": "12pt",
                                "bottom_margin": "12pt",
                            },
                        },
                        "settings": {"render_command": {"dont_generate_pdf": True}},
                    }
                )
                image = render_entry_figure(model, pathlib.Path(temporary))
                (directory / f"{entry_type}.png").write_bytes(image)


if __name__ == "__main__":
    main()
