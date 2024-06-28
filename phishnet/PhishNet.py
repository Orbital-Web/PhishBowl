from abc import ABCMeta, abstractmethod
from datasets import DatasetDict
from typing import TypedDict


class Emails(TypedDict):
    """A dictionary with fields "sender", "subject", and "body". Each field should have
    a list of strings of the same length, specifying each email's contents."""

    sender: list[str]
    subject: list[str]
    body: list[str]


class PhishNet(metaclass=ABCMeta):
    """A base class for detecting phishing emails."""

    @abstractmethod
    def rate(self, emails: Emails) -> list[float]:
        """Rates how likely the given emails are a phishing email.

        Args:
            emails (Emails): Group of emails to test.

        Returns:
            list[float]: Liklihood of each email being a phishing email.
        """
        pass

    def train(self, dataset: DatasetDict, *args, **kwargs):
        """Trains the PhishNet. Some nets may not need pre-training.

        Args:
            dataset (DatasetDict): Dataset to train on. Contains "train" and "test".
        """
        pass

    def reset(self):
        """Resets the PhishNet to the pre-trained state."""
        pass
