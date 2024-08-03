from abc import ABCMeta, abstractmethod
from typing import TypedDict

from .datastructs import TrainData


class Emails(TypedDict):
    """A dictionary representing multiple emails. Each field should be of the same
    length, with the same indices corresponding to the same email."""

    sender: list[str]
    subject: list[str]
    body: list[str]
    label: list[float]  # 1 for phishing, 0 for benign
    unsafe: list[bool]  # True if the email contains a caution or content blocked flag


class PhishNet(metaclass=ABCMeta):
    """A base class for detecting phishing emails."""

    @abstractmethod
    async def analyze(self, emails: Emails) -> list[float]:
        """Analyzes each email on whether they're a phish or not.

        Args:
            emails (Emails): Emails to analyze.

        Returns:
            list[float]: Likelihood of each email being a phish.
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
