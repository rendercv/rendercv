import json

import pytest

from rendercv.exception import RenderCVUserValidationError
from rendercv.schema.input_files import load_rendercv_model


def test_file_selection_and_value_precedence_share_one_contract(tmp_path):
    def write(name, value):
        path = tmp_path / name
        path.write_text(json.dumps(value))
        return path

    main = write(
        "cv.yaml",
        {
            "cv": {"name": "Main"},
            "design": {"theme": "classic", "page": {"size": "a4"}},
            "settings": {"render_command": {"design": "main-design.yaml"}},
        },
    )
    write("main-design.yaml", {"design": {"theme": "moderncv"}})
    write("settings-design.yaml", {"design": {"theme": "harvard"}})
    settings = write(
        "settings.yaml",
        {"settings": {"render_command": {"design": "settings-design.yaml"}}},
    )
    selected = write("selected.yaml", {"design": {"theme": "opal"}})
    overlay = write("overlay.yaml", {"cv": {"name": "Overlay"}})

    assert load_rendercv_model(main).design.theme == "moderncv"
    assert load_rendercv_model(main, settings=settings).design.theme == "harvard"
    model = load_rendercv_model(
        main,
        settings=settings,
        design=selected,
        overlays=[overlay],
        overrides={"cv.name": "CLI"},
    )
    assert model.design.theme == "opal"
    assert model.cv.name == "CLI"
    assert set(model._input_paths) == {main, settings, selected, overlay}


@pytest.mark.parametrize("role", ["design", "locale", "overlays"])
def test_general_overlays_cannot_change_the_load_plan(tmp_path, role):
    main = tmp_path / "cv.yaml"
    main.write_text("cv:\n  name: Jane\n")
    overlay = tmp_path / "private.yaml"
    overlay.write_text(
        json.dumps({"settings": {"render_command": {role: "other.yaml"}}})
    )
    with pytest.raises(RenderCVUserValidationError, match="cannot select input files"):
        load_rendercv_model(main, overlays=[overlay])
