from abc import ABCMeta, abstractmethod
from typing import TypedDict


class Emails(TypedDict):
    """A dictionary representing multiple emails. Each field should be of the same
    length, with the same indices corresponding to the same email."""

    sender: list[str]
    subject: list[str]
    body: list[str]
    label: list[float]  # 1 for phishing, 0 for benign


class PhishNet(metaclass=ABCMeta):
    """A base class for detecting phishing emails."""

    @abstractmethod
    async def analyze(self, emails: Emails) -> list[float]:
        """Analyzes each email on whether they're a phish or not.

        Args:
            emails (Emails): Emails to analyze.

        Returns:
            list[float]: Liklihood of each email being a phish.
        """
        pass

    def train(self, *args, **kwargs):
        """Trains the PhishNet. Some nets may not need pre-training."""
        pass

    def reset(self):
        """Resets the PhishNet to the pre-trained state."""
        pass
