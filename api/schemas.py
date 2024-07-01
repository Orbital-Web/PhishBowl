from pydantic import BaseModel, Field
from typing import Literal


class Email(BaseModel):
    sender: str
    subject: str
    body: str


class AnalysisResponse(BaseModel):
    label: Literal["LEGITIMATE", "PHISHING"]
    confidence: float = Field(None, ge=0, le=1)
