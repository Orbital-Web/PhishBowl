from models import Emails


class EmailTextProcessor:
    """A class for categorizing an email text into sender, subject, and body, as well as
    anonymization the email content."""

    def __init__(self):
        pass

    async def process(self, email_text: str) -> Emails:
        """Extract the email sender, subject, and body from the email text.

        Args:
            email_text (str): Text containing entire email content.

        Returns:
            Emails: Organized email object.
        """
        # TODO:
        return {"sender": [""], "subject": [""], "body": [email_text]}

    async def anonymize(self, emails: Emails) -> Emails:
        """Mask sensitive data from each email.

        Args:
            emails (Emails): Emails to anonymize.

        Returns:
            Emails: The anonymized emails.
        """
        # TODO:
        return emails
