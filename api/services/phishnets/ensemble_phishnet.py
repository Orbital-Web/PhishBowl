import asyncio
import logging

import numpy as np
from models import Emails, PhishNet, TrainData
from services.phishbowl import PhishBowl

from .gpt_phishnet import GPTPhishNet
from .semantic_phishnet import SemanticPhishNet

logger = logging.getLogger(__name__)


class EnsemblePhishNet(PhishNet):
    """PhishNet which combines the PhishBowl and FineTunedLLMPhishNet to detect phishing
    emails."""

    def __init__(self, phishbowl: PhishBowl = None):
        self.semantic_net = SemanticPhishNet(phishbowl)
        self.gpt_net = GPTPhishNet()

    async def analyze(self, emails: Emails) -> list[float]:
        scores = await asyncio.gather(
            self.semantic_net.analyze(emails), self.gpt_net.analyze(emails)
        )
        return np.mean(scores, axis=0)

    def train(self, traindata: TrainData):
        logger.warning("Training is not supported on the EnsemblePhishNet")
