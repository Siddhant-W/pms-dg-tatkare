from fastapi import HTTPException, status

class ConflictException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class FieldValidationError(HTTPException):
    """Submitted values are invalid (422), with one message per field.

    The ``detail`` is an object (not a bare string) so clients can show each
    message next to its input: ``{"code", "message", "errors": [{"field", "message"}]}``.
    """

    def __init__(self, errors: list[dict], message: str = "Some values are not valid."):
        super().__init__(
            status_code=422,
            detail={"code": "validation_error", "message": message, "errors": errors},
        )


class CodedConflictError(HTTPException):
    """A clash with existing data (409) that clients can recognise by ``code``."""

    def __init__(self, code: str, message: str, conflicts: list[dict] | None = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": code, "message": message, "conflicts": conflicts or []},
        )
