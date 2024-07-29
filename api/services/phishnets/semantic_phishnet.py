import asyncio
import logging

from models import Emails, PhishNet, TrainData
from services.phishbowl import PhishBowl, load_phishbowl

logger = logging.getLogger(__name__)


class SemanticPhishNet(PhishNet):
    """PhishNet which uses the PhishBowl to semantically detect phishing emails."""

    def __init__(self, phishbowl: PhishBowl = None):
        self.phishbowl = phishbowl
        if not phishbowl:
            logger.warning("PhishBowl not provided, loading a new instance.")
            self.phishbowl = asyncio.run(load_phishbowl())

    async def analyze(self, emails: Emails) -> list[float]:
        return await self.phishbowl.analyze_emails(emails)

    def train(self, traindata: TrainData):
        # asyncio.run(self.phishbowl.add_dataset(traindata.datasetdict["train"]))
        logger.warning("Training is not supported on the PhishBowlPhishNet")

    def reset(self):
        # asyncio.run(self.phishbowl.clear())
        pass
