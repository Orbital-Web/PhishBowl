import asyncio
import logging
import os

from huggingface_hub import AsyncInferenceClient, login
from models import Emails, PhishNet, TrainData
from services.textprocessing import EmailTextProcessor
from transformers import BertTokenizer

logger = logging.getLogger(__name__)


class HFBERTPhishNet(PhishNet):
    """PhishNet which uses a fine-tuned BERT provided by the huggingfaces inference API
    to detect phishing emails. Note this method easily reaches the request limit when
    using a free API token."""

    def __init__(self):
        login(token=os.environ.get("HUGGINGFACE_TOKEN_READ"))
        self.client = AsyncInferenceClient(model="ealvaradob/bert-finetuned-phishing")
        self.email_processor = EmailTextProcessor(target_tokens=512)
        self.tokenizer: BertTokenizer = BertTokenizer.from_pretrained(
            "ealvaradob/bert-finetuned-phishing"
        )

    async def analyze(self, emails: Emails) -> list[float]:
        # tokenize and decode to prevent going over the token limit as there aren't any
        # options to enable truncation using the client, or take tokens as input
        # if it's stupid but it works, it isn't stupid...
        documents = self.email_processor.to_text(emails)
        tokens = self.tokenizer(documents, truncation=True, max_length=508)
        truncated_documents = self.tokenizer.batch_decode(
            tokens["input_ids"], skip_special_tokens=True
        )

        predictions = await asyncio.gather(
            *[self.client.text_classification(doc) for doc in truncated_documents]
        )
        return [
            preds[0]["score"] if preds[0]["label"][0] == "p" else 1 - preds[0]["score"]
            for preds in predictions
        ]

    def train(self, traindata: TrainData):
        logger.warning("Training is not supported on the HFLLMPhishNet")
