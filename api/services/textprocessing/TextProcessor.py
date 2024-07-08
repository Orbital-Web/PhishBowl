from models import Emails


class EmailTextProcessor:
    """A class for processing and converting emails."""

    def __init__(self):
        self.token_limit = 512
        self.tokens_per_chr = 0.25  # approximate number of tokens per chr (with spaces)

    def from_text(self, email_text: str) -> Emails:
        """Extract the email sender, subject, and body from the email text.

        Args:
            email_text (str): Text containing entire email content.

        Returns:
            Emails: Organized email object.
        """
        # TODO:
        return {"sender": [""], "subject": [""], "body": [email_text]}

    def to_text(self, emails: Emails) -> list[str]:
        """Converts emails to a list of formatted texts.

        Args:
            emails (Emails): Emails to convert.

        Returns:
            list[str]: Formatted text for each email.
        """
        documents = []
        for subject, body in zip(emails["subject"], emails["body"]):
            # only add subject too if it'll likely fit in the token limit
            n_tokens = (len(body) + len(subject)) * self.tokens_per_chr
            documents.append(
                f"{subject}: {body}" if n_tokens <= self.token_limit else body
            )
        return documents

    def anonymize(self, emails: Emails) -> Emails:
        """Mask sensitive data from each email.

        Args:
            emails (Emails): Emails to anonymize.

        Returns:
            Emails: The anonymized emails.
        """
        # TODO:
        return emails
