from phishnet.PhishNet import PhishNet, Emails
from transformers import AutoTokenizer
from datasets import DatasetDict
import logging

logging.basicConfig(level=logging.DEBUG)


class FineTunedLLMPhishNet(PhishNet):
    """PhishNet which uses a fine-tuned LLM trained on a phishing email dataset to
    detect phishing emails."""

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            "distilbert/distilbert-base-uncased"
        )

    def rateScreenshots(self, files) -> list[float]:
        return 1

    def rate(self, emails: Emails) -> list[float]:
        return 0

    def train(self, dataset: DatasetDict):
        pass

    def reset(self):
        pass

    def tokenizeEmails(self, emails: Emails):
        texts = [
            f"From: {sender or 'unknown'}\nSubject: {subject}\nBody: {body}"
            for sender, subject, body in zip(
                emails["sender"], emails["subject"], emails["body"]
            )
        ]
        return self.tokenizer(texts, truncation=True)
