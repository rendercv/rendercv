import pathlib
import shutil

import typst

# Compiling the rendercv Typst package makes Typst download the packages it imports,
# at the versions it imports, into the directory that RenderCV ships them from:
renderer_path = pathlib.Path(__file__).parent.parent / "src" / "rendercv" / "renderer"
typst_packages_path = renderer_path / "typst_packages"
shutil.rmtree(typst_packages_path, ignore_errors=True)
typst.compile(
    renderer_path / "rendercv_typst" / "lib.typ",
    package_cache_path=typst_packages_path,
)
print("Typst packages downloaded successfully.")  # NOQA: T201
