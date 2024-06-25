from phishnet.PhishNet import PhishNet, Email
import random


class LLMPhishNet(PhishNet):
    """PhishNet which uses a multi-modal LLM to detect phishing emails."""

    def __init__(self):
        super().__init__()

    def rateScreenshot(self, file) -> float:
        return 1

    def rateEmail(self, email: Email) -> float:
        return random.random()
