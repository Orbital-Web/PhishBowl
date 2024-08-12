import hashlib
import logging
import os

from datasets import IterableDataset
from models import Emails
from services.textprocessing import EmailTextProcessor

from .azure_db import AzureDB

logger = logging.getLogger(__name__)


class PhishBowl:
    """A class for handling the phishing email dataset."""

    def __init__(self):
        self.db = AzureDB()
        self.text_processor = EmailTextProcessor(
            max_tokens=8191,
            truncate_method="content-end",
            tokenizer_model="text-embedding-3-small",
        )
        self.batchsize = 64  # batchsize of emails to ingest at once
        self.debug = os.getenv("env", "prod") != "prod"

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
            emails = self.text_processor.anonymize(emails)
        documents = self.text_processor.to_text(emails)
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

        await self.db.collection.add(documents=documents, metadatas=metadatas, ids=ids)
        if self.debug:
            total_count = await self.db.collection.count()
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
            return await self.db.collection.count()
        # return only those that match filter
        matches = await self.db.collection.get(include=[], where=where)
        return len(matches["ids"])

    async def clear(self):
        """Removes all documents from the phishbowl. Use with care."""
        await self.db.clear()

    async def delete_emails(self, emails: Emails, anonymize: bool = False):
        """Removes the emails from the phishbowl.

        Args:
            emails (Emails): Emails to remove.
            anonymize (bool, optional): Whether the email content was anonymized when
                added
        """
        processed_emails = self.process_emails(emails, anonymize)
        ids = processed_emails["id"]
        await self.db.collection.delete(ids=ids)


async def load_phishbowl() -> PhishBowl:
    """Creates a fully initialized phishbowl."""
    phishbowl = PhishBowl()
    await phishbowl.db.initialize_db()
    return phishbowl
