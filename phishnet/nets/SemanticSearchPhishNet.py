from phishnet.PhishNet import PhishNet, Email
import chromadb
from chromadb.utils import embedding_functions
import hashlib
from scipy.special import softmax
import numpy as np


class SemanticSearchPhishNet(PhishNet):
    """PhishNet which first extracts the text from the screenshot and searches the
    content against other emails in the PhishBowl to detect phishing emails.
    """

    def __init__(self):
        self.client = chromadb.PersistentClient(path="phishnet/database")
        self.collection = self.client.get_or_create_collection(
            name="SSPN",
            # embedding_functions=embedding_functions.SentenceTransformerEmbeddingFunction(
            #     model_name="Salesforce/SFR-Embedding-2_R"
            # ),
            metadata={"hnsw:space": "l2"},
        )
        self.comparison_size = 12

    def rateScreenshots(self, files) -> list[float]:
        return 1

    def rateEmails(self, emails: list[Email]) -> list[float]:
        matches = self.collection.query(
            query_texts=self.formatEmails(emails),
            n_results=self.comparison_size,
            include=["metadatas", "distances"],
        )

        phish_scores = []
        for similarities, metadatas in zip(matches["distances"], matches["metadatas"]):
            weights = softmax(-1 * np.array(similarities))  # using l2, smaller = closer
            scores = [metadata["phish_score"] for metadata in metadatas]
            phish_scores.append(np.dot(weights, scores))
        return phish_scores

    def train(self, emails: list[Email]) -> float:
        documents = self.formatEmails(emails)
        metadatas = [{"phish_score": email.phish_score} for email in emails]
        ids = [hashlib.sha256(doc.encode("utf-8")).hexdigest() for doc in documents]

        self.collection.add(
            documents=self.formatEmails(emails), metadatas=metadatas, ids=ids
        )

    def reset(self):
        self.client.delete_collection(name="SSPN")

    @staticmethod
    def formatEmails(emails: list[Email]) -> list[str]:
        """Formats a list of emails to be encoded.

        Args:
            emails (list[Email]): List of emails to format.

        Returns:
            list[str]: Formatted string of each email.
        """
        return [
            f"From: {email.sender or 'unknown'}\nSubject: {email.subject}\nBody: {email.body}"
            for email in emails
        ]
