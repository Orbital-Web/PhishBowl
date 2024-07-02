import chromadb
from chromadb.utils import embedding_functions
from models import Emails
from datasets import Dataset
from services.textprocessing import EmailTextProcessor
from scipy.special import softmax
import numpy as np
import hashlib
import logging

logger = logging.getLogger(__name__)


class PhishBowl:
    """A class for handling the phishing email dataset."""

    def __init__(self):
        self.collection_name = "phishbowl"
        self.client = None
        self.collection = None
        self.email_processor = EmailTextProcessor()
        self.batchsize = 2048  # batchsize of emails to ingest at once
        self.comparison_size = 12  # number of emails to use as reference when analyzing
        self.confidence_decay = 0.5  # positive value specifying how fast the confidence decays with distance

    async def initialize_db(self):
        """Initializes the client and collection used to store documents."""
        self.client = await chromadb.AsyncHttpClient(host="chromadb", port=5000)
        self.collection = await self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="avsolatorio/GIST-small-Embedding-v0"
            ),
            metadata={"hnsw:space": "l2"},
        )

    async def ingest_emails(self, emails: Emails, anonymize: bool = False):
        """Ingests the passed emails.

        Args:
            emails (Emails): Emails to ingest.
            anonymize (bool, optional): Whether to anonymize the emails first before
                ingesting. Defaults to False.
        """
        if anonymize:
            documents = await self.email_processor.anonymize(emails)

        documents = await self.email_processor.to_text(emails)
        metadatas = [{"label": label} for label in emails["label"]]
        ids = [hashlib.sha256(doc.encode("utf-8")).hexdigest() for doc in documents]

        await self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
        total_count = await self.collection.count()
        logger.info(f"Ingested {total_count} documents")

    async def ingest_dataset(self, dataset: Dataset, anonymize: bool = False):
        """Ingests emails in a dataset.

        Args:
            dataset (Dataset): Dataset of emails to ingest.
            anonymize (bool, optional): Whether to anonymize the emails first before
                ingesting. Defaults to False.
        """
        for i in range(0, dataset.num_rows, self.batchsize):
            emails = dataset[i : i + self.batchsize]
            await self.ingest_emails(emails, anonymize)

    async def clear_database(self):
        """Removes all documents from the database. Use with care."""
        await self.client.delete_collection(self.collection_name)
        await self.initialize_db()

    async def analyze_emails(self, emails: Emails) -> list[float]:
        """Compares the passed emails to the emails in the phishbowl and returns a score
        between 0 and 1 for each email on their liklihood of being a phish.

        Args:
            emails (Emails): Emails to analyze.

        Returns:
            list[float]: Liklihood of each email being a phish.
        """
        # get both phishing and benign emails to ensure both sets are represented
        documents = await self.email_processor.to_text(emails)
        matches = await self.collection.query(
            query_texts=documents,
            n_results=self.comparison_size,
            include=["metadatas", "distances"],
        )

        # calculate phish score for each email
        phish_scores = []
        for distances, metadatas in zip(matches["distances"], matches["metadatas"]):
            confidence = np.exp(-self.confidence_decay * distances[0])
            weights = softmax(-1 * np.array(distances))
            scores = [metadata["label"] for metadata in metadatas]

            phish_score = confidence * np.dot(weights, scores)
            phish_scores.append(phish_score)

        return phish_scores


async def load_phishbowl() -> PhishBowl:
    """Fully initializes and returns a PhishBowl"""
    phishbowl = PhishBowl()
    await phishbowl.initialize_db()
    return phishbowl
