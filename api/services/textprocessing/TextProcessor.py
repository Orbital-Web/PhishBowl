from models import Emails


class EmailTextProcessor:
    """A class for processing and converting emails."""

    def __init__(self, target_tokens: int = 512):
        self.target_tokens = target_tokens
        self.tokens_per_chr = 0.2815  # approximate number of tokens per string length

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
        for sender, subject, body in zip(
            emails["sender"], emails["subject"], emails["body"]
        ):
            sender = f"From: {sender.strip()}\n" if sender else ""
            subject = f"Subject: {subject.strip()}\n" if subject else ""
            body = body.strip()

            # only add header if it'll likely fit in the token limit
            tbody = len(body) * self.tokens_per_chr
            tsender = len(sender) * self.tokens_per_chr
            tsubject = len(subject) * self.tokens_per_chr
            if tbody + tsender > self.target_tokens:
                documents.append(body)
            elif tbody + tsender + tsubject > self.target_tokens:
                documents.append(sender + body)
            else:
                documents.append(sender + subject + body)
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
