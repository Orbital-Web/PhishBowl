from models import Emails


class EmailTextProcessor:
    """A class for processing and converting emails."""

    def __init__(self):
        pass

    async def from_text(self, email_text: str) -> Emails:
        """Extract the email sender, subject, and body from the email text.

        Args:
            email_text (str): Text containing entire email content.

        Returns:
            Emails: Organized email object.
        """
        # TODO:
        return {"sender": [""], "subject": [""], "body": [email_text]}

    async def to_text(self, emails: Emails) -> list[str]:
        """Converts emails to a list of formatted texts.

        Args:
            emails (Emails): Emails to convert.

        Returns:
            list[str]: Formatted text for each email.
        """
        return [
            f"From: {sender or 'unknown'}\nSubject: {subject}\nBody: {body}"
            for sender, subject, body in zip(
                emails["sender"], emails["subject"], emails["body"]
            )
        ]

    async def anonymize(self, emails: Emails) -> Emails:
        """Mask sensitive data from each email.

        Args:
            emails (Emails): Emails to anonymize.

        Returns:
            Emails: The anonymized emails.
        """
        # TODO:
        return emails
