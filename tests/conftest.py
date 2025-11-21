import pathlib

import pytest


@pytest.fixture
def testdata_dir(request):
    module_path = pathlib.Path(request.node.module.__file__)
    module_name = module_path.stem
    base_dir = module_path.parent

    return base_dir / "testdata" / module_name
