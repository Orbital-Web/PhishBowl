from phishnet.PhishNet import PhishNet, Email
import chromadb
from chromadb.utils import embedding_functions


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

    def rateScreenshot(self, file) -> float:
        return 1

    def rateEmail(self, email: Email) -> float:
        return 0

    def train(self, emails: list[Email]) -> float:
        self.collection.add(
            documents=self.formatEmails(emails),
            metadatas=[{"phish_score": email.phish_score} for email in emails],
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
