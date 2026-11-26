"""The API's single exception boundary.

Why:
    Guardrails ("Inside code"): one centralized boundary translates domain
    errors (`RenderCVUserError` family) into structured 422 responses reusing
    the core's own error data, and turns everything else into an opaque 500
    with a server-side logged id -- never a leaked stack trace.
"""

import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from rendercv.exception import (
    RenderCVUserError,
    RenderCVUserValidationError,
    RenderCVValidationError,
)

from .documents import DocumentPatchError
from .models import (
    CvConflictCurrent,
    CvConflictResponse,
    InternalErrorResponse,
    PatchOpErrorDetail,
    PatchOpErrorResponse,
    ValidationErrorItem,
    ValidationErrorResponse,
)

logger = logging.getLogger("rendercv_web")


class CvConflictError(Exception):
    """Raised when an autosave write loses the optimistic-concurrency check.

    Why:
        Translated into a `409` carrying the server's current state (see
        `cvs.py`) so the client can reconcile instead of silently
        overwriting -- or being silently overwritten by -- a concurrent
        write (guardrail: no last-write-wins).
    """

    def __init__(self, current: CvConflictCurrent) -> None:
        """Store the current server-side state to return to the client.

        Args:
            current: The CV's current `updated_at` and documents.
        """
        super().__init__("Autosave conflict: the CV changed since it was last read.")
        self.current = current


def validation_error_to_item(error: RenderCVValidationError) -> ValidationErrorItem:
    """Convert one core validation error into the API's error shape.

    Args:
        error: Structured validation error produced by the core.

    Returns:
        API-facing validation error item.
    """
    return ValidationErrorItem(
        location=".".join(error.schema_location) if error.schema_location else None,
        message=error.message,
        yaml_source=error.yaml_source,
        yaml_line=error.yaml_location[0][0] if error.yaml_location else None,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register the API's single exception boundary on the FastAPI app.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(RenderCVUserValidationError)
    async def handle_validation_error(
        request: Request, exc: RenderCVUserValidationError
    ) -> JSONResponse:
        """Translate structured core validation errors into a 422 response."""
        del request
        body = ValidationErrorResponse(
            errors=[validation_error_to_item(error) for error in exc.validation_errors]
        )
        return JSONResponse(status_code=422, content=body.model_dump())

    @app.exception_handler(RenderCVUserError)
    async def handle_user_error(
        request: Request, exc: RenderCVUserError
    ) -> JSONResponse:
        """Translate a single core user error into a 422 response."""
        del request
        body = ValidationErrorResponse(
            errors=[
                ValidationErrorItem(
                    location=None,
                    message=exc.message or "Invalid input.",
                    yaml_source="main_yaml_file",
                    yaml_line=None,
                )
            ]
        )
        return JSONResponse(status_code=422, content=body.model_dump())

    @app.exception_handler(DocumentPatchError)
    async def handle_patch_op_error(
        request: Request, exc: DocumentPatchError
    ) -> JSONResponse:
        """Translate a failed patch operation into a 400 response."""
        del request
        body = PatchOpErrorResponse(
            error=PatchOpErrorDetail(op_index=exc.op_index, message=exc.message)
        )
        return JSONResponse(status_code=400, content=body.model_dump())

    @app.exception_handler(CvConflictError)
    async def handle_cv_conflict_error(
        request: Request, exc: CvConflictError
    ) -> JSONResponse:
        """Translate a lost autosave race into a 409 with the current state."""
        del request
        body = CvConflictResponse(current=exc.current)
        return JSONResponse(status_code=409, content=body.model_dump(mode="json"))

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        """Turn any unhandled exception into an opaque 500 response.

        Why:
            Never leak stack traces or internal details to the client; the
            full exception is logged server-side under the same id.
        """
        del request
        error_id = uuid.uuid4().hex
        logger.exception(
            "Unhandled %s in rendercv-web (error_id=%s)",
            type(exc).__name__,
            error_id,
        )
        body = InternalErrorResponse(error_id=error_id)
        return JSONResponse(status_code=500, content=body.model_dump())
