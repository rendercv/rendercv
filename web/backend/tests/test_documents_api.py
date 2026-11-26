"""Contract tests for the comment-preserving YAML document endpoints.

Why:
    `POST /api/documents/parse` and `POST /api/documents/patch` back the
    form editor's two-way sync with the raw YAML editor
    (docs/plans/completed/cv-editor-web-app.md, Phase 2); the whole point is
    that patching through the form must not disturb the user's comments,
    key order, or quoting style, so those properties are asserted
    explicitly alongside the usual contract-test matrix (per the
    api-implementation skill).
"""

import concurrent.futures

import pytest
from fastapi.testclient import TestClient
from rendercv_web.app import app
from rendercv_web.models import MAX_DOCUMENT_BYTES

# A CV document deliberately shaped to exercise every fidelity property the
# patch endpoint must preserve: (a) a full-line comment above a section,
# (b) an inline comment after a field, (c) unusual key order (email before
# name), (d) a custom-titled section (not one of the built-in section keys).
FIDELITY_YAML = (
    "cv:\n"
    "  email: john@example.com  # inline comment\n"
    "  name: John Doe\n"
    "  sections:\n"
    "    # Custom section for volunteering\n"
    "    Volunteering:\n"
    "      - company: Helping Hands\n"
    "        highlights:\n"
    "          - Organized *weekend* food drives\n"
    "          - Trained new volunteers\n"
)

GENERIC_YAML = (
    "cv:\n"
    "  name: John Doe\n"
    "  sections:\n"
    "    experience:\n"
    "      - company: Acme\n"
    "        highlights:\n"
    "          - Did a thing\n"
    "          - Did another thing\n"
)


@pytest.fixture
def client() -> TestClient:
    """A FastAPI test client for the app."""
    return TestClient(app)


class TestParse:
    """Contract tests for `POST /api/documents/parse`."""

    def test_happy_path_returns_parsed_mapping(self, client: TestClient) -> None:
        response = client.post("/api/documents/parse", json={"yaml": GENERIC_YAML})

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["cv"]["name"] == "John Doe"
        assert body["data"]["cv"]["sections"]["experience"][0]["company"] == "Acme"

    def test_data_is_json_safe(self, client: TestClient) -> None:
        response = client.post("/api/documents/parse", json={"yaml": FIDELITY_YAML})

        assert response.status_code == 200
        data = response.json()["data"]
        # Plain str/dict/list all the way down -- no ruamel scalar-string or
        # CommentedMap/CommentedSeq types leak into the JSON body.
        assert isinstance(data["cv"]["email"], str)
        assert data["cv"]["email"] == "john@example.com"
        highlights = data["cv"]["sections"]["Volunteering"][0]["highlights"]
        assert highlights == [
            "Organized *weekend* food drives",
            "Trained new volunteers",
        ]

    def test_invalid_yaml_syntax_returns_422_same_shape_as_validate(
        self, client: TestClient
    ) -> None:
        response = client.post(
            "/api/documents/parse", json={"yaml": "cv:\n  name: [unterminated"}
        )

        assert response.status_code == 422
        body = response.json()
        assert body["errors"]
        error = body["errors"][0]
        assert error["yaml_source"] == "main_yaml_file"
        assert "not a valid YAML file" in error["message"]

    def test_oversized_document_returns_413(self, client: TestClient) -> None:
        oversized = "cv:\n  name: " + ("a" * (MAX_DOCUMENT_BYTES + 1)) + "\n"

        response = client.post("/api/documents/parse", json={"yaml": oversized})

        assert response.status_code == 413


class TestPatchFidelity:
    """The scenario required verbatim: one `set` op, everything else intact."""

    def test_set_changes_exactly_one_line_and_preserves_everything_else(
        self, client: TestClient
    ) -> None:
        response = client.post(
            "/api/documents/patch",
            json={
                "yaml": FIDELITY_YAML,
                "ops": [
                    {
                        "op": "set",
                        "path": [
                            "cv",
                            "sections",
                            "Volunteering",
                            0,
                            "highlights",
                            1,
                        ],
                        "value": "Trained 50 new volunteers",
                    }
                ],
            },
        )

        assert response.status_code == 200
        updated_yaml = response.json()["yaml"]

        before_lines = FIDELITY_YAML.splitlines()
        after_lines = updated_yaml.splitlines()

        assert len(before_lines) == len(after_lines)
        differing = [
            (i, b, a)
            for i, (b, a) in enumerate(zip(before_lines, after_lines, strict=True))
            if b != a
        ]
        assert differing == [
            (
                9,
                "          - Trained new volunteers",
                "          - Trained 50 new volunteers",
            )
        ]

        # Comments and key order survive verbatim.
        assert "  email: john@example.com  # inline comment" in after_lines
        assert "  name: John Doe" in after_lines
        assert after_lines.index("  email: john@example.com  # inline comment") < (
            after_lines.index("  name: John Doe")
        )
        assert "    # Custom section for volunteering" in after_lines
        assert "    Volunteering:" in after_lines


class TestPatchOps:
    """Contract tests for each `POST /api/documents/patch` op type."""

    def test_set_replaces_existing_scalar(self, client: TestClient) -> None:
        response = client.post(
            "/api/documents/patch",
            json={
                "yaml": GENERIC_YAML,
                "ops": [{"op": "set", "path": ["cv", "name"], "value": "Jane Doe"}],
            },
        )

        assert response.status_code == 200
        assert "  name: Jane Doe\n" in response.json()["yaml"]

    def test_set_creates_missing_final_key(self, client: TestClient) -> None:
        response = client.post(
            "/api/documents/patch",
            json={
                "yaml": GENERIC_YAML,
                "ops": [{"op": "set", "path": ["cv", "location"], "value": "Remote"}],
            },
        )

        assert response.status_code == 200
        assert "location: Remote" in response.json()["yaml"]

    def test_insert_appends_via_index_equal_len(self, client: TestClient) -> None:
        response = client.post(
            "/api/documents/patch",
            json={
                "yaml": GENERIC_YAML,
                "ops": [
                    {
                        "op": "insert",
                        "path": ["cv", "sections", "experience", 0, "highlights"],
                        "index": 2,
                        "value": "Shipped a third thing",
                    }
                ],
            },
        )

        assert response.status_code == 200
        lines = response.json()["yaml"].splitlines()
        highlight_lines = [line for line in lines if line.strip().startswith("- Did")]
        assert len(highlight_lines) == 2
        assert lines[-1].strip() == "- Shipped a third thing"

    def test_insert_creates_new_sequence_for_missing_key_at_index_zero(
        self, client: TestClient
    ) -> None:
        response = client.post(
            "/api/documents/patch",
            json={
                "yaml": GENERIC_YAML,
                "ops": [
                    {
                        "op": "insert",
                        "path": ["cv", "social_networks"],
                        "index": 0,
                        "value": {"network": "LinkedIn", "username": "johndoe"},
                    }
                ],
            },
        )

        assert response.status_code == 200
        updated_yaml = response.json()["yaml"]
        assert "social_networks:" in updated_yaml
        assert "network: LinkedIn" in updated_yaml

    def test_delete_removes_mapping_key(self, client: TestClient) -> None:
        response = client.post(
            "/api/documents/patch",
            json={
                "yaml": GENERIC_YAML,
                "ops": [
                    {
                        "op": "delete",
                        "path": ["cv", "sections", "experience", 0, "company"],
                    }
                ],
            },
        )

        assert response.status_code == 200
        assert "company: Acme" not in response.json()["yaml"]

    def test_delete_removes_sequence_element(self, client: TestClient) -> None:
        response = client.post(
            "/api/documents/patch",
            json={
                "yaml": GENERIC_YAML,
                "ops": [
                    {
                        "op": "delete",
                        "path": ["cv", "sections", "experience", 0, "highlights", 0],
                    }
                ],
            },
        )

        assert response.status_code == 200
        updated_yaml = response.json()["yaml"]
        assert "Did a thing" not in updated_yaml
        assert "Did another thing" in updated_yaml

    def test_move_reorders_sequence(self, client: TestClient) -> None:
        response = client.post(
            "/api/documents/patch",
            json={
                "yaml": GENERIC_YAML,
                "ops": [
                    {
                        "op": "move",
                        "path": ["cv", "sections", "experience", 0, "highlights"],
                        "from_index": 1,
                        "to_index": 0,
                    }
                ],
            },
        )

        assert response.status_code == 200
        lines = [
            line.strip()
            for line in response.json()["yaml"].splitlines()
            if line.strip().startswith("- Did")
        ]
        assert lines == ["- Did another thing", "- Did a thing"]


class TestPatchErrors:
    """400 error-shape contract tests for `POST /api/documents/patch`."""

    def test_bad_path_returns_400(self, client: TestClient) -> None:
        response = client.post(
            "/api/documents/patch",
            json={
                "yaml": GENERIC_YAML,
                "ops": [
                    {
                        "op": "set",
                        "path": ["cv", "sections", "experience", 5, "company"],
                        "value": "x",
                    }
                ],
            },
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["op_index"] == 0
        assert error["message"]

    def test_bad_index_returns_400(self, client: TestClient) -> None:
        response = client.post(
            "/api/documents/patch",
            json={
                "yaml": GENERIC_YAML,
                "ops": [
                    {
                        "op": "delete",
                        "path": ["cv", "sections", "experience", 0, "highlights", 5],
                    }
                ],
            },
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["op_index"] == 0
        assert "range" in error["message"]

    def test_set_with_missing_intermediate_returns_400(
        self, client: TestClient
    ) -> None:
        response = client.post(
            "/api/documents/patch",
            json={
                "yaml": GENERIC_YAML,
                "ops": [
                    {
                        "op": "set",
                        "path": [
                            "cv",
                            "sections",
                            "experience",
                            0,
                            "nonexistent",
                            "deeper",
                        ],
                        "value": "x",
                    }
                ],
            },
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["op_index"] == 0
        assert "not found" in error["message"]

    def test_invalid_yaml_syntax_returns_422(self, client: TestClient) -> None:
        response = client.post(
            "/api/documents/patch",
            json={
                "yaml": "cv:\n  name: [unterminated",
                "ops": [{"op": "set", "path": ["cv", "name"], "value": "x"}],
            },
        )

        assert response.status_code == 422
        body = response.json()
        assert body["errors"]
        assert body["errors"][0]["yaml_source"] == "main_yaml_file"

    def test_ops_are_atomic_second_op_failure_returns_no_partial_result(
        self, client: TestClient
    ) -> None:
        response = client.post(
            "/api/documents/patch",
            json={
                "yaml": GENERIC_YAML,
                "ops": [
                    {"op": "set", "path": ["cv", "name"], "value": "Jane Doe"},
                    {
                        "op": "set",
                        "path": ["cv", "sections", "experience", 99, "company"],
                        "value": "x",
                    },
                ],
            },
        )

        assert response.status_code == 400
        body = response.json()
        assert "yaml" not in body
        assert body["error"]["op_index"] == 1


class TestPatchSizeCap:
    """413 size-cap contract test for `POST /api/documents/patch`."""

    def test_oversized_document_returns_413(self, client: TestClient) -> None:
        oversized = "cv:\n  name: " + ("a" * (MAX_DOCUMENT_BYTES + 1)) + "\n"

        response = client.post(
            "/api/documents/patch",
            json={
                "yaml": oversized,
                "ops": [{"op": "set", "path": ["cv", "name"], "value": "x"}],
            },
        )

        assert response.status_code == 413


class TestConcurrentParsingThreadSafety:
    """Regression: shared ruamel instances corrupted under the threadpool.

    Why:
        /api/validate and /api/documents/parse both parse YAML on FastAPI's
        worker threads. Before the per-call parser fix (core
        `yaml_reader.build_yaml_parser` and this package's
        `build_document_yaml`), concurrent requests intermittently crashed
        with opaque 500s (AttributeError/ParserError inside ruamel).
    """

    def test_concurrent_validate_and_parse_requests_stay_200(
        self, client: TestClient
    ) -> None:
        sections = "\n".join(
            f"    section_{i}:\n      - entry one {i}\n      - entry two {i}"
            for i in range(30)
        )

        def hit_api(worker_index: int) -> list[int]:
            cv_yaml = (
                f"cv:\n  name: Worker {worker_index}\n  sections:\n" + sections + "\n"
            )
            statuses: list[int] = []
            for _ in range(10):
                response = client.post(
                    "/api/validate",
                    json={
                        "cv_yaml": cv_yaml,
                        "design_yaml": "",
                        "locale_yaml": "",
                        "settings_yaml": "",
                    },
                )
                statuses.append(response.status_code)
                response = client.post("/api/documents/parse", json={"yaml": cv_yaml})
                statuses.append(response.status_code)
            return statuses

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            all_statuses = [
                status
                for statuses in executor.map(hit_api, range(6))
                for status in statuses
            ]

        assert all_statuses == [200] * len(all_statuses)
