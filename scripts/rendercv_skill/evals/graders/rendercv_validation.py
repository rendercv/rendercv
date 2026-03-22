"""Deterministic grader: extract YAML from output, validate with RenderCV's pipeline.

Why:
    Every RenderCV skill response that includes YAML should produce valid,
    schema-compliant YAML. This grader uses RenderCV's own pydantic validation
    (the same pipeline as `rendercv render`) to catch syntax errors and schema
    violations before the LLM-as-judge even runs.
"""

import re

from rendercv.exception import RenderCVUserValidationError
from rendercv.schema.rendercv_model_builder import (
    build_rendercv_model_from_commented_map,
    read_yaml_with_validation_errors,
)


def extract_yaml_blocks(text: str) -> list[str]:
    """Extract YAML code blocks from markdown output."""
    return re.findall(r"```ya?ml\s*\n(.*?)```", text, re.DOTALL)


def get_assert(output: str, context: dict) -> dict:  # noqa: ARG001
    """Validate that output contains a parseable, schema-valid RenderCV YAML block.

    Args:
        output: The LLM's text response.
        context: promptfoo context (required by promptfoo, unused here).

    Returns:
        GradingResult dict with pass, score, and reason.
    """
    yaml_blocks = extract_yaml_blocks(output)

    if not yaml_blocks:
        return {
            "pass": False,
            "score": 0,
            "reason": "No YAML code block found in output.",
        }

    for i, block in enumerate(yaml_blocks):
        try:
            commented_map = read_yaml_with_validation_errors(block, "main_yaml_file")
            build_rendercv_model_from_commented_map(commented_map)
        except RenderCVUserValidationError as e:
            error_messages = "; ".join(err.message for err in e.validation_errors)
            return {
                "pass": False,
                "score": 0,
                "reason": (
                    f"YAML block {i + 1} fails RenderCV validation: {error_messages}"
                ),
            }

        return {
            "pass": True,
            "score": 1,
            "reason": "Valid RenderCV YAML.",
        }

    return {
        "pass": False,
        "score": 0,
        "reason": "No YAML code block found in output.",
    }
