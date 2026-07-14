from pydantic import BaseModel


class LipReadResponse(BaseModel):
    transcript: str
    confidence: float
    metrics: dict


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
