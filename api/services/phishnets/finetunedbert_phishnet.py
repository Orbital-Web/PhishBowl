import logging
import os

import evaluate
import numpy as np
import torch
from huggingface_hub import login
from models import Emails, PhishNet, TrainData
from services.textprocessing import EmailTextProcessor
from transformers import (
    BertForSequenceClassification,
    BertTokenizer,
    DataCollatorWithPadding,
    TextClassificationPipeline,
    Trainer,
    TrainingArguments,
)

logger = logging.getLogger(__name__)


class FineTunedBERTPhishNet(PhishNet):
    """PhishNet which uses a fine-tuned BERT trained on a phishing email dataset to
    detect phishing emails."""

    def __init__(self):
        login(token=os.environ.get("HUGGINGFACE_TOKEN_WRITE"))
        self.modelpath = "/app/services/phishnets/trained/bert-finetuned-phishing"
        self.batch_size = 1  # NOTE: device-specific, make sure to try different values
        self.email_processor = EmailTextProcessor(
            max_tokens=512, truncate_method="content"
        )
        self.classifier: TextClassificationPipeline = None
        self.model: BertForSequenceClassification = None
        self.tokenizer: BertTokenizer = None
        self.collator: DataCollatorWithPadding = None
        self.metrics = [
            evaluate.load("accuracy"),
            evaluate.load("precision"),
            evaluate.load("recall"),
        ]

        # load
        self.load_model()

    def load_model(self):
        """Loads the model, tokenizer, and the classification pipeline."""
        # first time training, load pre-trained model
        if not os.path.exists(self.modelpath):
            self.reset()

        # load fine-tuned model
        else:
            logger.info("Loading fine-tuned model...")
            self.model = BertForSequenceClassification.from_pretrained(self.modelpath)
            self.tokenizer = BertTokenizer.from_pretrained(self.modelpath)

        # get device
        is_cuda = torch.cuda.is_available()
        device = torch.device("cuda:0" if is_cuda else "cpu")
        self.model.to(device)

        # load pipeline
        logger.info(
            "Creating TextClassificationPipeline with:\n"
            + f"  device: {torch.cuda.get_device_name(device.index) if is_cuda else 'CPU'}\n"
            + f"  batch size: {self.batch_size}"
        )
        self.classifier = TextClassificationPipeline(
            model=self.model,
            tokenizer=self.tokenizer,
            batch_size=self.batch_size,
            device=device.index if is_cuda else -1,
        )

    async def analyze(self, emails: Emails) -> list[float]:
        predictions = self.classifier(
            self.email_processor.to_text(emails), truncation=True
        )
        return [
            pred["score"] if pred["label"][0] == "p" else 1 - pred["score"]
            for pred in predictions
        ]

    def train(self, traindata: TrainData):
        self.collator = DataCollatorWithPadding(tokenizer=self.tokenizer)
        tokenized_dataset = traindata.datasetdict.map(
            self.tokenize_emails, batched=True, batch_size=1024
        )
        training_args = TrainingArguments(
            output_dir=self.modelpath,
            learning_rate=2e-5,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            max_steps=2 * traindata.metadata["train"]["num_rows"],  # 2 epochs
            weight_decay=0.01,
            eval_steps=128,
            save_steps=128,
            eval_strategy="steps",
            save_strategy="steps",
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
        logger.info("Fine-tuning model...")
        trainer.train()

    def reset(self):
        logger.info("Downloading pre-trained base model...")
        self.model = BertForSequenceClassification.from_pretrained(
            "ealvaradob/bert-finetuned-phishing"
        )
        self.tokenizer = BertTokenizer.from_pretrained(
            "ealvaradob/bert-finetuned-phishing"
        )
        logger.info("Saving model...")
        self.model.save_pretrained(self.modelpath)
        self.tokenizer.save_pretrained(self.modelpath)

    def tokenize_emails(self, emails: Emails) -> dict[str, list]:
        """Tokenizes the emails to use for training. Intended to be used in the
        datasetdict map() function.

        Args:
            emails (Emails): Emails to tokenize.

        Returns:
            dict[str, list]: The email tokens.
        """
        documents = self.email_processor.to_text(emails)
        return self.tokenizer(documents, truncation=True)

    def compute_metrics(self, eval_pred: tuple[list, list]) -> dict[str, float]:
        """Computes the metrics defined in `self.metrics`. Intended to be used for
        model evaluation during training.

        Args:
            eval_pred (tuple[list, list]): A tuple of the model predictions and labels.

        Returns:
            dict[str, float]: Mapping of the metric name to the metric value.
        """
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        metrics = {}
        for metric in self.metrics:
            metrics.update(metric.compute(predictions=predictions, references=labels))
        return metrics
