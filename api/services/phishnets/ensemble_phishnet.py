import asyncio
import logging

import numpy as np
from models import Emails, PhishNet, TrainData
from services.phishbowl import PhishBowl

from .gpt_phishnet import GPTAnalysisResult, GPTPhishNet
from .semantic_phishnet import SemanticPhishNet

logger = logging.getLogger(__name__)


class EnsembleAnalysisResult(GPTAnalysisResult):
    semantic_confidence: float  # value between 1 and 0 for the confidence of the semantic phishnet, with 1 being the email is in the phishbowl


class EnsemblePhishNet(PhishNet):
    """PhishNet which combines the PhishBowl and FineTunedLLMPhishNet to detect phishing
    emails."""

    def __init__(self, phishbowl: PhishBowl = None):
        self.semantic_net = SemanticPhishNet(phishbowl)
        self.gpt_net = GPTPhishNet()

        self.weighting_function = lambda conf: 0.8 * np.sqrt(
            conf
        )  # weight of semantic results as a function of its confidence

    async def analyze(self, emails: Emails) -> list[EnsembleAnalysisResult]:
        ensemble_results = await asyncio.gather(
            self.semantic_net.analyze(emails), self.gpt_net.analyze(emails)
        )
        print("A")

        results: list[EnsembleAnalysisResult] = []
        for semantic_result, gpt_result in zip(*ensemble_results):
            semantic_confidence = semantic_result["confidence"]
            semantic_weight = self.weighting_function(semantic_confidence)
            score = np.clip(
                semantic_result["phishing_score"] * semantic_weight
                + gpt_result["phishing_score"] * (1 - semantic_weight),
                0.0,
                1.0,
            )
            results.append(
                {
                    "phishing_score": score,
                    "impersonating": gpt_result["impersonating"],
                    "reason": gpt_result["reason"],
                    "semantic_confidence": semantic_confidence,
                }
            )
        return results

    def train(self, traindata: TrainData):
        logger.warning("Training is not supported on the EnsemblePhishNet")
