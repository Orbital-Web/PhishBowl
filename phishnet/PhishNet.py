from abc import ABCMeta, abstractmethod


class Email:
    """A struct representing an email."""

    def __init__(
        self,
        subject: str = "",
        sender: str = "",
        body: str = "",
        phish_score: float = 0,
    ):
        self.subject: str = subject
        self.sender: str = sender
        self.body: str = body
        # utility
        self.phish_score: float = float(phish_score)


class PhishNet(metaclass=ABCMeta):
    """A base class for detecting phishing emails from a screenshot."""

    @abstractmethod
    def rateScreenshot(self, file) -> float:
        """Rates how likely the given screenshot contains a phishing email.

        Args:
            file (_type_): Screenshot of email to test.

        Returns:
            float: Liklihood of screenshot containing a phishing email.
        """
        pass

    @abstractmethod
    def rateEmail(self, email: Email) -> float:
        """Rates how likely a given email is a phishing email.

        Args:
            email (Email): Email to test.

        Returns:
            float: Liklihood of email being a phishing email.
        """
        pass

    def train(self, *args, **kwargs):
        """Trains the PhishNet. Some nets may not need pre-training."""
        pass

    def reset(self):
        """Resets the PhishNet to the pre-trained state."""
        pass
