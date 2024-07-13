from typing import Literal

from pydantic import BaseModel, Field


class Email(BaseModel):
    sender: str
    subject: str
    body: str


class LabeledEmail(BaseModel):
    sender: str
    subject: str
    body: str
    label: float = Field(None, ge=0, le=1)


class AnalysisResponse(BaseModel):
    label: Literal["LEGITIMATE", "PHISHING"]
    confidence: float = Field(None, ge=0, le=1)
