import pathlib

from rendercv.renderer.typst import render_typst_to_file
from rendercv.schema.rendercv_model_builder import build_rendercv_model

model = build_rendercv_model(pathlib.Path("test.yaml"))
render_typst_to_file(model)
