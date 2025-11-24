"""Tests to validate the test directory structure matches the source directory structure."""

import pathlib


def get_immediate_subdirectories(directory: pathlib.Path) -> set[str]:
    """Get immediate subdirectory names, excluding __pycache__ and testdata."""
    excluded = {"__pycache__", "testdata"}
    return {
        d.name
        for d in directory.iterdir()
        if d.is_dir() and d.name not in excluded
    }


def get_python_files(directory: pathlib.Path) -> set[str]:
    """Get all .py files in a directory, excluding conftest.py and __init__.py."""
    excluded_files = {"conftest.py", "__init__.py"}
    return {
        f.name
        for f in directory.iterdir()
        if f.is_file() and f.suffix == ".py" and f.name not in excluded_files
    }


def get_all_source_subdirs(root: pathlib.Path) -> set[pathlib.Path]:
    """Recursively get all subdirectories under root, excluding __pycache__."""
    subdirs = set()
    for path in root.rglob("*"):
        if path.is_dir() and "__pycache__" not in path.parts:
            subdirs.add(path.relative_to(root))
    return subdirs


def test_test_folders_match_source_structure():
    """Verify test folders that mirror source folders have no extra subfolders."""
    src_root = pathlib.Path(__file__).parent.parent.parent / "src" / "rendercv"
    tests_root = pathlib.Path(__file__).parent.parent

    source_subdirs = get_all_source_subdirs(src_root)
    invalid_folders = []

    for subdir in source_subdirs:
        test_dir = tests_root / subdir
        source_dir = src_root / subdir

        if not test_dir.exists():
            continue

        test_subfolders = get_immediate_subdirectories(test_dir)
        source_subfolders = get_immediate_subdirectories(source_dir)

        extra_folders = test_subfolders - source_subfolders
        for folder in extra_folders:
            invalid_folders.append(f"tests/{subdir}/{folder}")

    assert not invalid_folders, (
        "The following test folders do not have corresponding source folders:\n"
        + "\n".join(f"  - {f}" for f in sorted(invalid_folders))
    )


def test_all_test_files_follow_naming_pattern():
    """Verify all test files follow the pattern test_<source_filename>.py."""
    src_root = pathlib.Path(__file__).parent.parent.parent / "src" / "rendercv"
    tests_root = pathlib.Path(__file__).parent.parent

    source_subdirs = get_all_source_subdirs(src_root)
    invalid_test_files = []

    for subdir in source_subdirs:
        test_dir = tests_root / subdir
        source_dir = src_root / subdir

        if not test_dir.exists():
            continue

        test_files = get_python_files(test_dir)
        source_files = get_python_files(source_dir)

        for test_file in test_files:
            if not test_file.startswith("test_"):
                invalid_test_files.append(
                    f"tests/{subdir}/{test_file} - does not start with 'test_'"
                )
                continue

            expected_source_file = test_file[5:]  # Remove "test_" prefix
            if expected_source_file not in source_files:
                invalid_test_files.append(
                    f"tests/{subdir}/{test_file} - no corresponding source file "
                    f"src/rendercv/{subdir}/{expected_source_file}"
                )

    assert not invalid_test_files, (
        "The following test files violate the naming pattern:\n"
        + "\n".join(f"  - {f}" for f in sorted(invalid_test_files))
    )
