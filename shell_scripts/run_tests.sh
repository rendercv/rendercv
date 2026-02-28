#!/bin/bash
set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -a, --all           Run all tests (default)"
    echo "  -f, --file FILE     Run tests from a specific file (e.g. tests/test_data.py)"
    echo "  -k, --keyword EXPR  Run tests matching a keyword expression"
    echo "  -c, --coverage      Run tests with coverage report"
    echo "  -v, --verbose       Verbose output"
    echo "  -h, --help          Show this help message"
    exit 0
}

PYTEST_ARGS=()
COVERAGE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--all)       shift ;;
        -f|--file)      PYTEST_ARGS+=("$2"); shift 2 ;;
        -k|--keyword)   PYTEST_ARGS+=("-k" "$2"); shift 2 ;;
        -c|--coverage)  COVERAGE=true; shift ;;
        -v|--verbose)   PYTEST_ARGS+=("-v"); shift ;;
        -h|--help)      usage ;;
        *)              PYTEST_ARGS+=("$1"); shift ;;
    esac
done

echo "Running tests from: $REPO_DIR"
echo "---"

if $COVERAGE; then
    hatch run coverage run -m pytest "${PYTEST_ARGS[@]}" && \
    hatch run coverage combine 2>/dev/null || true && \
    hatch run coverage report && \
    hatch run coverage html --show-contexts
    echo "---"
    echo "HTML coverage report: $REPO_DIR/htmlcov/index.html"
else
    hatch run pytest "${PYTEST_ARGS[@]}"
fi