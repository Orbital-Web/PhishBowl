from abc import ABCMeta, abstractmethod
from typing import NotRequired, TypedDict

from .datastructs import TrainData


class Emails(TypedDict):
    """A dictionary representing multiple emails. Each field should be of the same
    length, with the same indices corresponding to the same email."""

    sender: list[str | None]
    subject: list[str | None]
    body: list[str]
    label: NotRequired[list[float]]  # 1 for phishing, 0 for benign
    unsafe: NotRequired[list[bool]]  # if email contains caution or content blocked flag
    text: NotRequired[list[str]]  # the processed email contents
    id: NotRequired[list[str]]  # the processed email ids


class RawAnalysisResult(TypedDict):
    """A dictionary for the analysis result of an email. There may be other information
    in the dictionary such as the confidence."""

    phishing_score: float  # 1 for phishing, 0 for benign


class PhishNet(metaclass=ABCMeta):
    """A base class for detecting phishing emails."""

    @abstractmethod
    async def analyze(self, emails: Emails) -> list[RawAnalysisResult]:
        """Analyzes each email on whether they're a phish or not.

        Args:
            emails (Emails): Emails to analyze.

        Returns:
            list[RawAnalysisResult]: Results of the analysis for each email.
        """
        pass

    def train(self, traindata: TrainData):
        """Trains the PhishNet. Some nets may not need pre-training.

        Args:
            traindata (TrainData): Data to train on.
        """
        pass

    def reset(self):
        """Resets the PhishNet to the pre-trained state."""
        pass
