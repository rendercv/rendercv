import os
import pathlib

import pytest
from hypothesis import settings as hypothesis_settings

hypothesis_settings.register_profile("default", max_examples=100, deadline=None)
hypothesis_settings.register_profile("ci", max_examples=200, deadline=None)
hypothesis_settings.register_profile(
    "stress", max_examples=1500, deadline=None, derandomize=True
)
# CI selects the "ci" profile with the HYPOTHESIS_PROFILE environment variable:
hypothesis_settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "default"))


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--update-testdata",
        action="store_true",
        default=False,
        help="Update the updatable testdata",
    )


@pytest.fixture
def update_testdata(request: pytest.FixtureRequest) -> bool:
    return request.config.getoption("--update-testdata")


@pytest.fixture
def testdata_dir(request: pytest.FixtureRequest) -> pathlib.Path:
    module_path = pathlib.Path(request.node.module.__file__)
    module_name = module_path.stem
    base_dir = module_path.parent

    return base_dir / "testdata" / module_name
