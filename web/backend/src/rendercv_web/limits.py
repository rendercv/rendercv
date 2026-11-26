"""Shared request-size guardrails (guardrails: "trust no one").

Why:
    Every YAML document that reaches the `rendercv` core, whether it arrives
    through `/api/validate`, `/api/render`, or the persistence endpoints in
    `cvs.py`, must be size-capped before it does -- a request body is
    attacker-controlled and the core assumes well-behaved input. Kept in its
    own module (rather than duplicated per router) so `app.py` and `cvs.py`
    enforce the exact same limit the exact same way.
"""

from fastapi import HTTPException

from .models import MAX_DOCUMENT_BYTES


def enforce_yaml_size_cap(yaml_text: str, field_name: str = "yaml") -> None:
    """Reject a single YAML document over the size cap before it reaches the core.

    Args:
        yaml_text: The document text to check.
        field_name: Name to report in the error detail.

    Raises:
        HTTPException: 413 if `yaml_text` exceeds `MAX_DOCUMENT_BYTES`.
    """
    if len(yaml_text.encode("utf-8")) > MAX_DOCUMENT_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"`{field_name}` exceeds the {MAX_DOCUMENT_BYTES} byte limit.",
        )


def enforce_documents_size_cap(documents: dict[str, str]) -> None:
    """Reject any single YAML document over the size cap before it reaches the core.

    Args:
        documents: Mapping of field name to YAML document text (e.g. the
            `model_dump()` of a four-document request/payload model).

    Raises:
        HTTPException: 413 if any document exceeds `MAX_DOCUMENT_BYTES`.
    """
    for field_name, value in documents.items():
        enforce_yaml_size_cap(value, field_name)
