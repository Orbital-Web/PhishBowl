from phishnet.PhishNet import PhishNet, Emails
from transformers import pipeline
from huggingface_hub import login
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logging.basicConfig(level=logging.DEBUG)


class PromptBasedLLMPhishNet(PhishNet):
    """PhishNet which uses passes the email along with a prompt to a multi-modal LLM to
    detect phishing emails."""

    def __init__(self):
        login(token=os.environ.get("HUGGINGFACE_TOKEN"))
        self.pipline = pipeline(
            "text-generation", model="mistralai/Mistral-7B-Instruct-v0.3"
        )
        self.prompt = (
            "I want you to act as a spam detector to determine whether a given email is a phishing email or a legitimate email. "
            + "Your analysis should be thorough and evidence-based. Phishing emails often impersonate legitimate brands and "
            + "use social engineering techniques to deceive users. These techniques include, but are not limited to: fake "
            + "rewards, fake warnings about account problems, and creating a sense of urgency or interest. Spoofing the sender "
            + "address and embedding deceptive HTML links are also common tactics. Analyze the email by following these steps:\n"
            + "1. Identify any impersonation of well-known brands.\n"
            + "2. Examine the email header for spoofing signs, such as discrepancies in the sender name or email address. "
            + "Evaluate the subject line for typical phishing characteristics (e.g., urgency, promise of reward). Note that "
            + "some emails may not contain any sender or subject.\n"
            + "3. Analyze the email body for social engineering tactics designed to induce clicks on hyperlinks. "
            + "Inspect URLs to determine if they are misleading or lead to suspicious websites.\n"
            + 'You must output your result as a JSON string in the form `{"score": SCORE}`, where SCORE is a 2-digit decimal '
            + "number between 0 and 1 indicating how likely the given email is a phishing email. Your output will be parsed and "
            + "type-checked against the aforementioned format, so make sure your output matches exactly! If there aren't enough "
            + "information to determine whether a given email is a phishing email or not, your output SCORE should be 0.00 to "
            + "avoid incorrectly marking legitimate emails as phishing."
        )

    def rate(self, emails: Emails) -> list[float]:
        for document in self.format_emails(emails):
            messages = [
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": document},
            ]
            response = self.chatbot(messages)
            print(response)
            exit()

    @staticmethod
    def format_emails(emails: Emails) -> list[str]:
        """Formats a list of emails to be encoded.

        Args:
            emails (Emails): Group of emails to format.

        Returns:
            list[str]: Formatted string of each email.
        """
        return [
            f"From: {sender or 'unknown'}\nSubject: {subject}\nBody: {body}"
            for sender, subject, body in zip(
                emails["sender"], emails["subject"], emails["body"]
            )
        ]
