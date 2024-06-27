from abc import ABCMeta, abstractmethod


class Email:
    """A struct representing an email."""

    def __init__(
        self,
        subject: str = "",
        sender: str = "",
        body: str = "",
        phish_score: float = 0.0,
    ):
        # email content
        self.subject: str = subject
        self.sender: str = sender
        self.body: str = body

        # metadata
        self.phish_score: float = float(phish_score)


class PhishNet(metaclass=ABCMeta):
    """A base class for detecting phishing emails from a screenshot."""

    @abstractmethod
    def rateScreenshots(self, files) -> list[float]:
        """Rates how likely the given screenshots contain a phishing email.

        Args:
            files (_type_): Screenshots of emails to test.

        Returns:
            float: Liklihood of each screenshot containing a phishing email.
        """
        pass

    @abstractmethod
    def rateEmails(self, emails: list[Email]) -> list[float]:
        """Rates how likely the given emails are a phishing email.

        Args:
            emails (list[Email]): Emails to test.

        Returns:
            list[float]: Liklihood of each email being a phishing email.
        """
        pass

    def train(self, *args, **kwargs):
        """Trains the PhishNet. Some nets may not need pre-training."""
        pass

    def reset(self):
        """Resets the PhishNet to the pre-trained state."""
        pass
