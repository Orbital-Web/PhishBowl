from phishnet.PhishNet import PhishNet, Email
import random


class LLMPhishNet(PhishNet):
    """PhishNet which uses a multi-modal LLM to detect phishing emails."""

    def __init__(self):
        super().__init__()

    def rateScreenshots(self, files) -> list[float]:
        return 1

    def rateEmails(self, email: list[Email]) -> list[float]:
        return random.random()
