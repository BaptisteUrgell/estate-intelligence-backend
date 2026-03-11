from typing import Any

from pydantic import BaseModel, Field


class ProblemDetails(BaseModel):
    type: str = Field(default="about:blank", description="URI identifying the error type.")
    title: str = Field(..., description="Short, human-readable summary of the problem.")
    status: int = Field(..., description="The HTTP status code.")
    detail: str = Field(..., description="Human-readable explanation specific to this occurrence.")
    instance: str | None = Field(
        None, description="URI reference identifying the specific occurrence (e.g., Request ID)."
    )

    # Custom extensions
    error_code: str | None = Field(None, description="Internal domain error code.")
    invalid_params: list[dict[str, Any]] | None = Field(
        None, description="List of validation errors."
    )
