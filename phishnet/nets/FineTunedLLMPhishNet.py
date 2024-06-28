from phishnet.PhishNet import PhishNet, Emails
from transformers import AutoTokenizer
from huggingface_hub import login
from dotenv import load_dotenv
import os
import logging

load_dotenv()

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

    def rateEmails(self, emails: Emails) -> list[float]:
        return 0

    def train(self, *args, **kwargs):
        pass

    def reset(self):
        pass
