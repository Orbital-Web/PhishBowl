from models import Emails, PhishNet
from huggingface_hub import login
from transformers import (
    AutoTokenizer,
    DataCollatorWithPadding,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    pipeline,
)
from datasets import DatasetDict
import evaluate
import numpy as np
import os
import logging


logger = logging.getLogger(__name__)


class FineTunedLLMPhishNet(PhishNet):
    """PhishNet which uses a fine-tuned LLM trained on a phishing email dataset to
    detect phishing emails."""

    def __init__(self):
        login(token=os.environ.get("HUGGINGFACE_TOKEN_WRITE"))
        self.tokenizer = AutoTokenizer.from_pretrained(
            "distilbert/distilbert-base-uncased"
        )
        self.collator = DataCollatorWithPadding(tokenizer=self.tokenizer)
        self.metrics = {"accuracy": evaluate.load("accuracy")}
        self.id2label = {0: "LEGITIMATE", 1: "PHISHING"}
        self.label2id = {"LEGITIMATE": 0, "PHISHING": 1}
        self.model_path = "services/phishnets/FineTunedLLMPhishNet/models/FTLLMPN"
        self.model = None
        self.classifier = None

    async def analyze(self, emails: Emails) -> list[float]:
        if not self.classifier:
            self.classifier = pipeline("text-classification", model=self.model_path)
        prediction = self.classifier(self.format_emails(emails))
        return [self.label2id(pred["label"]) * pred["score"] for pred in prediction]

    def train(self, dataset: DatasetDict):
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "distilbert/distilbert-base-uncased",
            num_labels=2,
            id2label=self.id2label,
            label2id=self.label2id,
        )
        tokenized_dataset = dataset.map(self.tokenize_emails, batched=True)
        training_args = TrainingArguments(
            output_dir=self.model_path,
            learning_rate=2e-5,
            per_device_train_batch_size=32,
            per_device_eval_batch_size=32,
            num_train_epochs=2,
            weight_decay=0.01,
            eval_strategy="steps",
            eval_steps=64,
            save_strategy="steps",
            save_steps=64,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
        )
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset["train"],
            eval_dataset=tokenized_dataset["test"],
            tokenizer=self.tokenizer,
            data_collator=self.collator,
            compute_metrics=self.compute_metrics,
        )
        trainer.train()

    def reset(self):
        pass

    @staticmethod
    def format_emails(emails: Emails) -> list[str]:
        """Formats a list of emails to be encoded.

        Args:
            emails (Emails): Group of emails to format.

        Returns:
            list[str]: Formatted string of each email.
        """
        return [
            f"From: {sender or 'unknown'}\nSubject: {subject}\nBody: {body}"
            for sender, subject, body in zip(
                emails["sender"], emails["subject"], emails["body"]
            )
        ]

    def tokenize_emails(self, emails: Emails):
        texts = self.format_emails(emails)
        return self.tokenizer(texts, truncation=True)

    def compute_metrics(self, eval_pred):
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        return self.metrics["accuracy"].compute(
            predictions=predictions, references=labels
        )
