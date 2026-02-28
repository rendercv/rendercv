#!/bin/bash
set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

DEFAULT_INPUT="$REPO_DIR/example_files/rick_full.yaml"
OUTPUT_FOLDER="rendercv_output"

usage() {
    echo "Usage: $0 [options] [input_file]"
    echo ""
    echo "Runs rendercv render against an input YAML file."
    echo "Output goes to: $OUTPUT_FOLDER/"
    echo ""
    echo "Arguments:"
    echo "  input_file           Path to a YAML input file (default: example_files/rick_full.yaml)"
    echo ""
    echo "Options:"
    echo "  -l, --list           List available example input files"
    echo "  -h, --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                              # Run with default example"
    echo "  $0 example_files/rick_full.yaml                 # Run with a specific example"
    echo "  $0 /path/to/my_cv.yaml                          # Run with your own input"
    exit 0
}

list_examples() {
    echo "Available example inputs:"
    for f in "$REPO_DIR/example_files"/*.yaml "$REPO_DIR/example_files"/*.json "$REPO_DIR/examples"/*.yaml; do
        [[ -f "$f" ]] && echo "  $(realpath --relative-to="$REPO_DIR" "$f")"
    done
    exit 0
}

INPUT_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -l|--list)  list_examples ;;
        -h|--help)  usage ;;
        *)          INPUT_FILE="$1"; shift ;;
    esac
done

if [[ -z "$INPUT_FILE" ]]; then
    INPUT_FILE="$DEFAULT_INPUT"
fi

if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: Input file not found: $INPUT_FILE"
    exit 1
fi

echo "Running rendercv render with: $INPUT_FILE"
echo "Output folder: $OUTPUT_FOLDER/"
echo "---"
hatch run rendercv render "$INPUT_FILE" --output-folder-name "$OUTPUT_FOLDER"
