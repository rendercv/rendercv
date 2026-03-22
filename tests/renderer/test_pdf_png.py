import pathlib
from unittest.mock import MagicMock, patch

import pytest

from rendercv.exception import RenderCVInternalError
from rendercv.renderer.pdf_png import generate_pdf, generate_png, get_package_path
from rendercv.renderer.typst import generate_typst
from rendercv.schema.models.design.built_in_design import available_themes
from rendercv.schema.models.rendercv_model import RenderCVModel


@pytest.mark.parametrize("theme", available_themes)
@pytest.mark.parametrize("cv_variant", ["minimal", "full"])
def test_generate_pdf(
    compare_file_with_reference,
    theme: str,
    cv_variant: str,
    request: pytest.FixtureRequest,
):
    base_model = request.getfixturevalue(f"{cv_variant}_rendercv_model")

    model = RenderCVModel(
        cv=base_model.cv,
        design={"theme": theme},
        locale=base_model.locale,
        settings=base_model.settings,
    )

    def generate_file(output_path):
        model.settings.render_command.typst_path = output_path.with_suffix(".typ")
        typst_path = generate_typst(model)

        model.settings.render_command.pdf_path = output_path
        generate_pdf(model, typst_path)

    reference_filename = f"{theme}_{cv_variant}.pdf"

    assert compare_file_with_reference(generate_file, reference_filename)


@pytest.mark.parametrize("theme", available_themes)
def test_generate_png(
    compare_file_with_reference,
    theme: str,
    minimal_rendercv_model: RenderCVModel,
):
    model = RenderCVModel(
        cv=minimal_rendercv_model.cv,
        design={"theme": theme},
        locale=minimal_rendercv_model.locale,
        settings=minimal_rendercv_model.settings,
    )

    def generate_file(output_path):
        model.settings.render_command.typst_path = output_path.with_suffix(".typ")
        typst_path = generate_typst(model)

        model.settings.render_command.png_path = output_path
        generate_png(model, typst_path)

    reference_filename = f"{theme}_minimal.png"

    assert compare_file_with_reference(generate_file, reference_filename)


class TestGetPackagePath:
    def test_creates_correct_directory_structure(self):
        get_package_path.cache_clear()
        result = get_package_path()

        # Find the version-named directory under preview/rendercv/:
        rendercv_package_dir = result / "preview" / "rendercv"
        assert rendercv_package_dir.is_dir()

        version_dirs = list(rendercv_package_dir.iterdir())
        assert len(version_dirs) == 1

        package_dir = version_dirs[0]
        assert (package_dir / "typst.toml").is_file()
        assert (package_dir / "lib.typ").is_file()

    def test_returns_cached_result(self):
        get_package_path.cache_clear()
        first_result = get_package_path()
        second_result = get_package_path()
        assert first_result == second_result

    def test_raises_error_when_version_missing_from_typst_toml(self):
        get_package_path.cache_clear()
        toml_without_version = '[package]\nname = "rendercv"\n'
        with (
            patch("pathlib.Path.read_text", return_value=toml_without_version),
            pytest.raises(
                RenderCVInternalError,
                match=r"Could not find version in",
            ),
        ):
            get_package_path()


class TestGeneratePngCleansUpOldFiles:
    def test_removes_stale_png_files_from_previous_run(
        self,
        tmp_path: pathlib.Path,
        minimal_rendercv_model: RenderCVModel,
    ):
        model = RenderCVModel(
            cv=minimal_rendercv_model.cv,
            design={"theme": "classic"},
            locale=minimal_rendercv_model.locale,
            settings=minimal_rendercv_model.settings,
        )
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "John_Doe_CV_1.png").write_bytes(b"old")
        (output_dir / "John_Doe_CV_2.png").write_bytes(b"old")
        (output_dir / "John_Doe_CV_3.png").write_bytes(b"old")

        model.settings.render_command.typst_path = output_dir / "John_Doe_CV.typ"
        typst_path = generate_typst(model)
        model.settings.render_command.png_path = output_dir / "John_Doe_CV.png"
        result = generate_png(model, typst_path)

        assert result is not None
        all_pngs = list(output_dir.glob("John_Doe_CV_*.png"))
        assert len(all_pngs) == len(result)

    def test_does_not_remove_unrelated_files(
        self,
        tmp_path: pathlib.Path,
        minimal_rendercv_model: RenderCVModel,
    ):
        model = RenderCVModel(
            cv=minimal_rendercv_model.cv,
            design={"theme": "classic"},
            locale=minimal_rendercv_model.locale,
            settings=minimal_rendercv_model.settings,
        )
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "John_Doe_CV_1.png").write_bytes(b"old")
        (output_dir / "unrelated_file.png").write_bytes(b"old")
        (output_dir / "Other_CV_1.png").write_bytes(b"old")

        model.settings.render_command.typst_path = output_dir / "John_Doe_CV.typ"
        typst_path = generate_typst(model)
        model.settings.render_command.png_path = output_dir / "John_Doe_CV.png"
        generate_png(model, typst_path)

        assert (output_dir / "unrelated_file.png").exists()
        assert (output_dir / "Other_CV_1.png").exists()

    def test_works_when_no_old_files_exist(
        self,
        tmp_path: pathlib.Path,
        minimal_rendercv_model: RenderCVModel,
    ):
        model = RenderCVModel(
            cv=minimal_rendercv_model.cv,
            design={"theme": "classic"},
            locale=minimal_rendercv_model.locale,
            settings=minimal_rendercv_model.settings,
        )
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        model.settings.render_command.typst_path = output_dir / "John_Doe_CV.typ"
        typst_path = generate_typst(model)
        model.settings.render_command.png_path = output_dir / "John_Doe_CV.png"
        result = generate_png(model, typst_path)

        assert result is not None
        assert len(result) >= 1


def test_raises_error_when_typst_returns_none_bytes(
    tmp_path: pathlib.Path,
    minimal_rendercv_model: RenderCVModel,
):
    model = RenderCVModel(
        cv=minimal_rendercv_model.cv,
        design={"theme": "classic"},
        locale=minimal_rendercv_model.locale,
        settings=minimal_rendercv_model.settings,
    )
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    model.settings.render_command.typst_path = output_dir / "John_Doe_CV.typ"
    typst_path = generate_typst(model)
    model.settings.render_command.png_path = output_dir / "John_Doe_CV.png"

    mock_compiler = MagicMock()
    mock_compiler.compile.return_value = [None]

    with (
        patch(
            "rendercv.renderer.pdf_png.get_typst_compiler", return_value=mock_compiler
        ),
        pytest.raises(RenderCVInternalError, match="Typst compiler returned None"),
    ):
        generate_png(model, typst_path)
