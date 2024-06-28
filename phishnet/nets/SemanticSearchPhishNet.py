from phishnet.PhishNet import PhishNet, Emails
from datasets import DatasetDict
import chromadb
from chromadb.utils import embedding_functions
import hashlib
from scipy.special import softmax
import numpy as np
import logging

logger = logging.getLogger(__name__)


class SemanticSearchPhishNet(PhishNet):
    """PhishNet which first extracts the text from the screenshot and searches the
    content against other emails in the PhishBowl to detect phishing emails.
    """

    def __init__(self):
        self.client = chromadb.PersistentClient(path="phishnet/database")
        self.initialize_collection()
        self.train_batchsize = 2048
        self.comparison_size = 12

    def rate(self, emails: Emails) -> list[float]:
        matches = self.collection.query(
            query_texts=self.format_emails(emails),
            n_results=self.comparison_size,
            include=["metadatas", "distances"],
        )

        phish_scores = []
        for similarities, metadatas in zip(matches["distances"], matches["metadatas"]):
            weights = softmax(-1 * np.array(similarities))  # using l2, smaller = closer
            scores = [metadata["phish_score"] for metadata in metadatas]
            phish_scores.append(np.dot(weights, scores))
        return phish_scores

    def train(self, dataset: DatasetDict):
        dataset["train"] = dataset["train"].map(
            self.preprocess_training_emails, batched=True
        )
        for i in range(0, dataset["train"].num_rows, self.train_batchsize):
            batch = dataset["train"][i : i + self.train_batchsize]
            documents = batch["text"]
            metadatas = [{"phish_score": label} for label in batch["label"]]
            ids = [hashlib.sha256(doc.encode("utf-8")).hexdigest() for doc in documents]
            self.collection.add(documents=documents, metadatas=metadatas, ids=ids)

            logger.info(f"Ingested {i + self.train_batchsize} documents")

    def reset(self):
        self.client.delete_collection(name="SSPN")
        self.initialize_collection()

    def initialize_collection(self):
        """Builds a collection to store embeddings."""
        self.collection = self.client.get_or_create_collection(
            name="SSPN",
            # embedding_functions=embedding_functions.SentenceTransformerEmbeddingFunction(
            #     model_name="Salesforce/SFR-Embedding-2_R"
            # ),
            metadata={"hnsw:space": "l2"},
        )

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

    @staticmethod
    def preprocess_training_emails(emails: Emails) -> Emails:
        """Formats a single email in place to be encoded. The formatted email is placed
        in a new `text` column.

        Args:
            email (Emails): Group of emails to format.

        Returns:
            Emails: Modified emails with their formatted text.
        """
        emails["text"] = SemanticSearchPhishNet.format_emails(emails)
        return emails
