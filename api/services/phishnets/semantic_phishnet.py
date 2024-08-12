import asyncio
import logging

import numpy as np
from models import Emails, PhishNet, RawAnalysisResult, TrainData
from scipy.special import softmax
from services.phishbowl import PhishBowl, load_phishbowl

logger = logging.getLogger(__name__)


class SemanticAnalysisResult(RawAnalysisResult):
    confidence: float  # value between 1 and 0 for the confidence


class SemanticPhishNet(PhishNet):
    """PhishNet which uses the PhishBowl to semantically detect phishing emails."""

    def __init__(self, phishbowl: PhishBowl = None):
        self.phishbowl = phishbowl
        if not phishbowl:
            logger.warning("PhishBowl not provided, loading a new instance.")
            self.phishbowl = asyncio.run(load_phishbowl())

        self.comparison_size = 12  # number of emails to use as reference when analyzing
        self.confidence_decay = 0.8  # positive value specifying how fast the confidence decays with distance
        self.dispersion = 0.001  # positive value with smaller values putting more weight to distances near 0

    async def analyze(self, emails: Emails) -> list[SemanticAnalysisResult]:
        # make sure the phishbowl is not empty
        db_count = await self.phishbowl.count()
        if db_count == 0:
            return [{"phishing_score": 0.0, "confidence": 0.0} for _ in emails["body"]]

        # get both phishing and benign emails to ensure both sets are represented
        documents = self.phishbowl.text_processor.to_text(emails)
        matches = await self.phishbowl.db.collection.query(
            query_texts=documents,
            n_results=self.comparison_size,
            include=["metadatas", "distances"],
        )

        # calculate phish score for each email
        results: list[SemanticAnalysisResult] = []
        for distances, metadatas in zip(matches["distances"], matches["metadatas"]):
            confidence = np.exp(-self.confidence_decay * distances[0] * distances[0])
            reciprocals = 1.0 / (np.array(distances) + self.dispersion)
            weights = reciprocals / np.sum(reciprocals)
            scores = [metadata["label"] for metadata in metadatas]

            score = confidence * np.dot(weights, scores)
            results.append({"phishing_score": score, "confidence": confidence})

        return results

    def train(self, traindata: TrainData):
        # asyncio.run(self.phishbowl.add_dataset(traindata.datasetdict["train"]))
        logger.warning("Training is not supported on the PhishBowlPhishNet")

    def reset(self):
        # asyncio.run(self.phishbowl.clear())
        pass
