import logging
import re

import dns.resolver
from models import Emails, PhishNet, RawAnalysisResult, TrainData

logger = logging.getLogger(__name__)


class SenderPhishNet(PhishNet):
    """PhishNet which uses heuristics based approaches on the sender address to detect
    phishing emails."""

    def __init__(self):
        self.mailname_re = re.compile(
            r"\b([a-zA-Z0-9._%+-]+)@(?:[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b|$"
        )  # regex to extract email name
        self.maildomain_re = re.compile(
            r"\b[a-zA-Z0-9._%+-]+@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b|$"
        )  # regex to extract email domain
        with open("/app/services/phishnets/data/spam-domains.txt", "r") as f:
            self.spam_domains = set(line.strip() for line in f)

    async def analyze(self, emails: Emails) -> list[RawAnalysisResult]:
        senders = await self.split_senders(emails)

        results: list[RawAnalysisResult] = []
        for name, domain in senders:
            if not domain:
                results.append(0)
                continue
            mx_score = await self.check_mx_record(domain)
            domain_score = await self.check_domain_spam(domain)

            score = min(1.0, (mx_score + domain_score) / 2.0)
            results.append({"phishing_score": score})
        return results

    def train(self, traindata: TrainData):
        logger.warning("Training is not supported on the SenderPhishNet")

    async def split_senders(self, emails: Emails) -> list[tuple[str, str]]:
        """Splits the sender into email name and email domain.

        Args:
            emails (Emails): Emails to split.

        Returns:
            list[tuple[str, str]]: Email name and domain for each email.
        """
        return [
            (
                self.mailname_re.findall(sender)[0] if sender else "",
                self.maildomain_re.findall(sender)[0] if sender else "",
            )
            for sender in emails["sender"]
        ]

    async def check_mx_record(self, domain: str) -> int:
        try:
            record = dns.resolver.resolve(domain, "MX")
            return 0 if record else 1
        except Exception:
            return 1

    async def check_domain_spam(self, domain: str) -> int:
        return domain in self.spam_domains
