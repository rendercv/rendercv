import pathlib

import pytest


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
