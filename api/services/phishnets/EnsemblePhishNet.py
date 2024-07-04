from models import Emails, PhishNet
from datasets import IterableDatasetDict
from services.phishbowl import PhishBowl, load_phishbowl
import asyncio
import logging

logger = logging.getLogger(__name__)


class EnsemblePhishNet(PhishNet):
    def __init__(self, phishbowl: PhishBowl = None):
        self.phishbowl = phishbowl
        if not phishbowl:
            logger.warning("PhishBowl not provided, loading a new instance.")
            self.phishbowl = asyncio.run(load_phishbowl())

    async def analyze(self, emails: Emails) -> list[float]:
        return await self.phishbowl.analyze_emails(emails)

    def train(self, dataset: IterableDatasetDict):
        asyncio.run(self.phishbowl.add_dataset(dataset["train"]))

    def reset(self):
        asyncio.run(self.phishbowl.clear())
