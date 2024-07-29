import hashlib
import logging

import numpy as np
from chromadb.utils import embedding_functions
from datasets import IterableDataset
from models import Emails
from scipy.special import softmax
from services.textprocessing import EmailTextProcessor

import chromadb

logger = logging.getLogger(__name__)


class PhishBowl:
    """A class for handling the phishing email dataset."""

    def __init__(self):
        # database
        self.collection_name = "phishbowl"
        self.client = None
        self.collection = None
        self.email_processor = EmailTextProcessor(target_tokens=256)
        self.batchsize = 2048  # batchsize of emails to ingest at once
        # analysis
        self.comparison_size = 12  # number of emails to use as reference when analyzing
        self.confidence_decay = 0.8  # positive value specifying how fast the confidence decays with distance

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

    def process_emails(self, emails: Emails, anonymize: bool) -> dict[str, list]:
        """Returns the formatted email texts (optionally may be anonymized) and ids.
        Intended to be used in the dataset map() function.

        Args:
            emails (Emails): Emails to process.
            anonymize (bool): Whether to anonymize the emails or not.

        Returns:
            dict[str, list]: The processed email texts.
        """
        if anonymize:
            emails = self.email_processor.anonymize(emails)
        documents = self.email_processor.to_text(emails)
        ids = [hashlib.sha256(doc.encode("utf-8")).hexdigest() for doc in documents]
        return {"text": documents, "id": ids}

    async def add_emails(self, emails: Emails, anonymize: bool = False):
        """Adds the emails to the phishbowl.

        Args:
            emails (Emails): Emails to add.
            anonymize (bool, optional): Whether to anonymize the emails first before
                adding. Defaults to False.
        """
        # if called from `add_dataset()`, text and id is already generated
        if "text" in emails:
            documents = emails["text"]
            ids = emails["id"]

        # otherwise, generate text and id
        else:
            processed_emails = self.process_emails(emails, anonymize)
            documents = processed_emails["text"]
            ids = processed_emails["id"]

        metadatas = [{"label": label} for label in emails["label"]]

        await self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
        total_count = await self.collection.count()
        logger.info(f"Ingested {total_count} documents")

    async def add_dataset(self, dataset: IterableDataset, anonymize: bool = False):
        """Adds emails in the dataset to the phishbowl.

        Args:
            dataset (IterableDataset): Dataset of emails to add.
            anonymize (bool, optional): Whether to anonymize the emails first before
                adding. Defaults to False.
        """
        # process text in batches for speedup
        dataset = dataset.map(
            self.process_emails,
            fn_kwargs={"anonymize": anonymize},
            batched=True,
            batch_size=self.batchsize,
        )

        for emails in dataset.iter(self.batchsize):
            await self.add_emails(emails, anonymize)

    async def count(self, where: dict = None) -> int:
        """Returns the number of documents in the phishbowl. Count can be narrowed to
        searching only documents of a specific type by specifying metadata filters.

        Args:
            where (dict, optional): Metadata filter to count only certain types of
                documents. See https://docs.trychroma.com/guides#using-where-filters
                for documentation on metadata filters.

        Returns:
            int: Number of matches.
        """
        # return entire collection count
        if not where:
            return await self.collection.count()
        # return only those that match filter
        matches = await self.collection.get(include=[], where=where)
        return len(matches["ids"])

    async def clear(self):
        """Removes all documents from the phishbowl. Use with care."""
        await self.client.delete_collection(self.collection_name)
        await self.initialize_db()

    async def delete_emails(self, emails: Emails):
        """Removes the emails from the phishbowl.

        Args:
            emails (Emails): Emails to remove.
        """
        documents = self.email_processor.to_text(emails)
        ids = [hashlib.sha256(doc.encode("utf-8")).hexdigest() for doc in documents]
        await self.collection.delete(ids=ids)

    async def analyze_emails(self, emails: Emails) -> list[float]:
        """Compares the emails to the emails in the phishbowl and returns a score
        between 0 and 1 for each email's liklihood of being a phish.

        Args:
            emails (Emails): Emails to analyze.

        Returns:
            list[float]: Liklihood of each email being a phish.
        """
        # get both phishing and benign emails to ensure both sets are represented
        documents = self.email_processor.to_text(emails)
        matches = await self.collection.query(
            query_texts=documents,
            n_results=self.comparison_size,
            include=["metadatas", "distances"],
        )

        # calculate phish score for each email
        phish_scores = []
        for distances, metadatas in zip(matches["distances"], matches["metadatas"]):
            confidence = np.exp(-self.confidence_decay * distances[0] * distances[0])
            weights = softmax(-1 * np.array(distances))
            scores = [metadata["label"] for metadata in metadatas]

            phish_score = confidence * np.dot(weights, scores)
            phish_scores.append(phish_score)

        return phish_scores


async def load_phishbowl() -> PhishBowl:
    """Creates a fully initialized phishbowl."""
    phishbowl = PhishBowl()
    await phishbowl.initialize_db()
    return phishbowl
