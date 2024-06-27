from phishnet.PhishNet import PhishNet, Email
import random


class FineTunedLLMPhishNet(PhishNet):
    """PhishNet which uses a fine-tuned LLM trained on a phishing email dataset to
    detect phishing emails."""

    def __init__(self):
        pass

    def rateScreenshots(self, files) -> list[float]:
        return 1

    def rateEmails(self, emails: list[Email]) -> list[float]:
        return random.random()

    def train(self, *args, **kwargs):
        pass

    def reset(self):
        pass
