"""Comment-preserving YAML parse and patch for the editor's raw-YAML view.

Why:
    Phase 2 of the web editor plan needs the form editor and the raw YAML
    editor to stay in sync without losing the user's comments, key order,
    or quoting style. `rendercv.schema.yaml_reader` already parses YAML the
    way the core pipeline does (custom scanner so `*` in Markdown bullets
    isn't treated as a YAML alias, timestamps kept as strings); this module
    adds a second ruamel.yaml instance with the *same* read semantics plus
    `preserve_quotes=True` so a document can also be dumped back out
    byte-identical except for the edits actually requested
    (docs/plans/completed/cv-editor-web-app.md, Phase 2).
"""

import io
from dataclasses import dataclass
from typing import Any

import ruamel.yaml
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.scanner import RoundTripScanner

from rendercv.exception import RenderCVUserValidationError, RenderCVValidationError
from rendercv.schema.rendercv_model_builder import get_yaml_error_location

from .models import DeleteOp, InsertOp, MoveOp, PatchOp, SetOp


class ScannerNoAlias(RoundTripScanner):
    """Treat `*` as a plain scalar character instead of alias syntax.

    Why:
        Mirrors `rendercv.schema.yaml_reader.ScannerNoAlias` exactly: a
        document that validates through the core must also parse here, or
        editing a CV full of Markdown `*bold*`/`*italic*` would break the
        patch endpoint even though `/api/validate` accepts it.
    """

    def fetch_alias(self) -> None:
        """Treat `*` as a plain scalar character instead of alias syntax."""
        self.fetch_plain()


def build_document_yaml() -> ruamel.yaml.YAML:
    """Build the round-trip YAML instance used to read and dump documents.

    Why:
        `preserve_quotes` must be set before the instance's constructor is
        first touched -- ruamel bakes it into the `RoundTripConstructor` at
        construction time, so setting it after (e.g. after registering the
        timestamp override) would silently have no effect. A large `width`
        avoids ruamel re-wrapping long lines that the user never touched,
        and `indent(mapping=2, sequence=4, offset=2)` matches the
        indentation already used throughout this repo's `examples/*.yaml`
        (dash indented under its key, not flush with it), so newly inserted
        content looks native rather than reformatting the whole file.

    Returns:
        A configured `ruamel.yaml.YAML` instance. Build one per operation:
        ruamel keeps mutable parser state on the instance, so sharing one
        across the threadpool that serves concurrent requests corrupts
        parses (the same thread-safety bug fixed in the core's
        `yaml_reader.build_yaml_parser`).
    """
    document_yaml = ruamel.yaml.YAML()
    document_yaml.Scanner = ScannerNoAlias
    document_yaml.preserve_quotes = True
    document_yaml.width = 1_000_000
    document_yaml.indent(mapping=2, sequence=4, offset=2)
    # Same as rendercv.schema.yaml_reader: keep timestamp-shaped scalars as
    # plain strings instead of letting ruamel construct `datetime.date`.
    document_yaml.constructor.yaml_constructors["tag:yaml.org,2002:timestamp"] = (
        lambda loader, node: loader.construct_scalar(node)
    )
    return document_yaml


@dataclass
class DocumentPatchError(Exception):
    """A single patch operation could not be applied.

    Why:
        Ops apply atomically: the API boundary (see `errors.py`) turns this
        into `{"error": {"op_index", "message"}}` and the caller never dumps
        a partially-patched document.
    """

    op_index: int
    message: str


def load_yaml_document(yaml_text: str) -> CommentedMap:
    """Parse a YAML document with the patch endpoint's fidelity settings.

    Why:
        Reuses `get_yaml_error_location` -- the same coordinate extraction
        the core uses for its own YAML syntax errors -- so a parse failure
        here produces the identical `{errors: [...]}` shape `/api/validate`
        returns, just via a different (quote-preserving) ruamel instance.

    Args:
        yaml_text: Raw YAML document text.

    Returns:
        The parsed document, ready for in-place patching.

    Raises:
        RenderCVUserValidationError: If the text isn't valid YAML, or is
            empty.
    """
    try:
        result = build_document_yaml().load(yaml_text)
    except ruamel.yaml.YAMLError as e:
        parser_message = str(e).splitlines()[0].strip()
        if not parser_message.endswith("."):
            parser_message += "."
        raise RenderCVUserValidationError(
            validation_errors=[
                RenderCVValidationError(
                    schema_location=None,
                    yaml_location=get_yaml_error_location(e),
                    yaml_source="main_yaml_file",
                    message=f"This is not a valid YAML file. {parser_message}",
                    input="...",
                )
            ]
        ) from e

    if result is None:
        raise RenderCVUserValidationError(
            validation_errors=[
                RenderCVValidationError(
                    schema_location=None,
                    yaml_location=None,
                    yaml_source="main_yaml_file",
                    message="This is not a valid YAML file. The input file is empty!",
                    input="...",
                )
            ]
        )

    return result


def to_json_safe(value: Any) -> Any:
    """Recursively convert a parsed ruamel document into plain JSON-safe data.

    Why:
        ruamel's `CommentedMap`/`CommentedSeq`/scalar-string subclasses
        carry comment and style metadata alongside the value; the parse
        endpoint must return plain `dict`/`list`/`str`/`int`/`float`/`bool`/
        `None` so every client-side JSON consumer works, without leaking
        ruamel-specific types.

    Args:
        value: Any node from a parsed ruamel document.

    Returns:
        The equivalent plain Python/JSON value.
    """
    if isinstance(value, dict):
        return {str(key): to_json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_json_safe(item) for item in value]
    if isinstance(value, str):
        return str(value)
    if value is None or isinstance(value, bool | int | float):
        return value
    return str(value)


def to_ruamel_value(value: Any) -> Any:
    """Convert a plain JSON value from a patch op into ruamel-native structure.

    Why:
        Patch op values arrive as plain `dict`/`list`/scalars from pydantic;
        wrapping nested dicts/lists as `CommentedMap`/`CommentedSeq` lets
        ruamel dump them with the same indentation settings as the rest of
        the document instead of falling back to a different representer.

    Args:
        value: A JSON-safe value from a patch operation.

    Returns:
        The same value, with nested dicts/lists as ruamel containers.
    """
    if isinstance(value, dict):
        result = CommentedMap()
        for key, item in value.items():
            result[key] = to_ruamel_value(item)
        return result
    if isinstance(value, list):
        sequence = CommentedSeq()
        for item in value:
            sequence.append(to_ruamel_value(item))
        return sequence
    return value


def navigate_existing(node: Any, path: list[str | int], op_index: int) -> Any:
    """Walk an already-existing path into a document.

    Args:
        node: The document (or sub-node) to start from.
        path: Path segments to walk; every segment must already exist.
        op_index: Index of the op this navigation is for, for error detail.

    Returns:
        The node found at the end of `path` (`node` itself if `path` is empty).

    Raises:
        DocumentPatchError: If any segment is missing, out of range, or the
            wrong type for the container it's applied to.
    """
    for segment in path:
        if isinstance(node, CommentedMap):
            if not isinstance(segment, str) or segment not in node:
                raise DocumentPatchError(
                    op_index, f"Path segment {segment!r} not found in mapping."
                )
            node = node[segment]
        elif isinstance(node, CommentedSeq):
            if not isinstance(segment, int) or not (0 <= segment < len(node)):
                raise DocumentPatchError(
                    op_index,
                    f"Path segment {segment!r} is not a valid sequence index.",
                )
            node = node[segment]
        else:
            raise DocumentPatchError(
                op_index, f"Cannot descend into a scalar value at {segment!r}."
            )
    return node


def resolve_parent_and_key(
    document: CommentedMap, path: list[str | int], op_index: int
) -> tuple[Any, str | int]:
    """Resolve the container and final key/index a path points at.

    Why:
        `set`, `delete`, `insert`, and `move` all address one element by
        its parent container plus the final path segment (the element
        itself may not exist yet, e.g. a `set` creating a new mapping key).

    Args:
        document: The root document.
        path: Non-empty path to resolve.
        op_index: Index of the op this resolution is for, for error detail.

    Returns:
        The parent container and the final path segment.

    Raises:
        DocumentPatchError: If `path` is empty or an intermediate segment
            doesn't exist.
    """
    if not path:
        raise DocumentPatchError(op_index, "`path` must not be empty.")
    parent = navigate_existing(document, path[:-1], op_index)
    return parent, path[-1]


def apply_set(document: CommentedMap, op: SetOp, op_index: int) -> None:
    """Apply a `set` operation in place.

    Args:
        document: The document being patched.
        op: The `set` operation.
        op_index: Index of this op in the request, for error detail.

    Raises:
        DocumentPatchError: If the path is invalid for `set`.
    """
    parent, last = resolve_parent_and_key(document, op.path, op_index)
    value = to_ruamel_value(op.value)

    if isinstance(parent, CommentedMap):
        if not isinstance(last, str):
            raise DocumentPatchError(op_index, "Mapping keys must be strings.")
        parent[last] = value
    elif isinstance(parent, CommentedSeq):
        if not isinstance(last, int) or not (0 <= last < len(parent)):
            raise DocumentPatchError(
                op_index, f"Index {last!r} is out of range for `set`."
            )
        parent[last] = value
    else:
        raise DocumentPatchError(op_index, "Cannot `set` inside a scalar value.")


def apply_insert(document: CommentedMap, op: InsertOp, op_index: int) -> None:
    """Apply an `insert` operation in place.

    Args:
        document: The document being patched.
        op: The `insert` operation.
        op_index: Index of this op in the request, for error detail.

    Raises:
        DocumentPatchError: If the path doesn't resolve to a sequence (or a
            missing key insertable at index 0), or the index is out of range.
    """
    parent, last = resolve_parent_and_key(document, op.path, op_index)

    if isinstance(parent, CommentedMap):
        if not isinstance(last, str):
            raise DocumentPatchError(op_index, "Mapping keys must be strings.")
        if last not in parent:
            if op.index != 0:
                raise DocumentPatchError(
                    op_index,
                    f"Cannot insert at index {op.index} into a missing sequence.",
                )
            parent[last] = CommentedSeq()
        target = parent[last]
    elif isinstance(parent, CommentedSeq):
        if not isinstance(last, int) or not (0 <= last < len(parent)):
            raise DocumentPatchError(
                op_index, f"Index {last!r} is out of range for `insert`."
            )
        target = parent[last]
    else:
        raise DocumentPatchError(op_index, "Cannot descend into a scalar value.")

    if not isinstance(target, CommentedSeq):
        raise DocumentPatchError(op_index, "Path does not resolve to a sequence.")
    if not (0 <= op.index <= len(target)):
        raise DocumentPatchError(
            op_index, f"Index {op.index} is out of range for `insert`."
        )
    target.insert(op.index, to_ruamel_value(op.value))


def apply_delete(document: CommentedMap, op: DeleteOp, op_index: int) -> None:
    """Apply a `delete` operation in place.

    Args:
        document: The document being patched.
        op: The `delete` operation.
        op_index: Index of this op in the request, for error detail.

    Raises:
        DocumentPatchError: If the path doesn't resolve to an existing key
            or sequence element.
    """
    parent, last = resolve_parent_and_key(document, op.path, op_index)

    if isinstance(parent, CommentedMap):
        if not isinstance(last, str) or last not in parent:
            raise DocumentPatchError(op_index, f"Key {last!r} not found.")
        del parent[last]
    elif isinstance(parent, CommentedSeq):
        if not isinstance(last, int) or not (0 <= last < len(parent)):
            raise DocumentPatchError(
                op_index, f"Index {last!r} is out of range for `delete`."
            )
        del parent[last]
    else:
        raise DocumentPatchError(op_index, "Cannot `delete` inside a scalar value.")


def apply_move(document: CommentedMap, op: MoveOp, op_index: int) -> None:
    """Apply a `move` operation in place.

    Args:
        document: The document being patched.
        op: The `move` operation.
        op_index: Index of this op in the request, for error detail.

    Raises:
        DocumentPatchError: If the path doesn't resolve to a sequence, or
            either index is out of range.
    """
    target = navigate_existing(document, op.path, op_index)
    if not isinstance(target, CommentedSeq):
        raise DocumentPatchError(op_index, "Path does not resolve to a sequence.")

    length = len(target)
    if not (0 <= op.from_index < length):
        raise DocumentPatchError(
            op_index, f"`from_index` {op.from_index} is out of range."
        )
    if not (0 <= op.to_index < length):
        raise DocumentPatchError(op_index, f"`to_index` {op.to_index} is out of range.")

    value = target.pop(op.from_index)
    target.insert(op.to_index, value)


def apply_patch_ops(yaml_text: str, ops: list[PatchOp]) -> str:
    """Parse `yaml_text`, apply `ops` in order, and dump the result back out.

    Why:
        The whole point of this endpoint is fidelity: only the requested
        edits should show up in the returned YAML, with every comment, key
        order, and quoting style the user had intact.

    Args:
        yaml_text: The YAML document to patch.
        ops: Ordered patch operations to apply.

    Returns:
        The updated YAML document text.

    Raises:
        RenderCVUserValidationError: If `yaml_text` isn't valid YAML.
        DocumentPatchError: If any op fails; no op after it is applied and
            nothing is dumped.
    """
    document = load_yaml_document(yaml_text)

    for op_index, op in enumerate(ops):
        if isinstance(op, SetOp):
            apply_set(document, op, op_index)
        elif isinstance(op, InsertOp):
            apply_insert(document, op, op_index)
        elif isinstance(op, DeleteOp):
            apply_delete(document, op, op_index)
        elif isinstance(op, MoveOp):
            apply_move(document, op, op_index)

    stream = io.StringIO()
    build_document_yaml().dump(document, stream)
    return stream.getvalue()
