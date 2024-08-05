from typing import Literal

import tiktoken
from models import Emails


class EmailTextProcessor:
    """A class for processing and truncating emails."""

    truncate_methods = Literal["none", "end", "content", "content-end"]

    def __init__(
        self,
        max_tokens: int = 512,
        truncate_method: truncate_methods = "none",
        tokenizer_model: None | str = None,
    ):
        self.max_tokens = max_tokens
        self.method: EmailTextProcessor.truncate_methods = truncate_method
        self.tokenizer = (
            None
            if tokenizer_model is None
            else tiktoken.encoding_for_model(tokenizer_model)
        )
        self.tokens_per_chr = 0.2815  # approx no. of tokens per char

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
        if "label" in emails:  # training
            documents = [
                self.truncate(sender, subject, body, label)
                for sender, subject, body, label in zip(
                    emails["sender"],
                    emails["subject"],
                    emails["body"],
                    emails["label"],
                )
            ]
        else:  # testing
            documents = [
                self.truncate(sender, subject, body, None)
                for sender, subject, body in zip(
                    emails["sender"],
                    emails["subject"],
                    emails["body"],
                )
            ]
        return documents

    def truncate(
        self, sender: str | None, subject: str | None, body: str, label: float | None
    ) -> str:
        """Truncates the email content string to be below self.max_tokens.
        Truncation strategy depends on self.method and self.tokenizer.
        Method:
            - none: no truncation, tokenizer is ignored
            - end: truncate (label + sender + subject + body) from the end
            - content: always keep body, include label, sender, and subject if they fit
            - content-end: apply content then end
        Tokenizer:
            - None: estimate token count based on string length
            - Encoding: use a particular tokenizer to get the exact token count

        Args:
            sender (str | None): email sender info
            subject (str | None): email subject line
            body (str): email body
            label (float | None): email label, may be when processing unseen text

        Returns:
            str: The truncated email string
        """
        label = (
            f"This is a {['benign', 'phishing'][label >= 0.5]} email:\n"
            if label is not None
            else ""
        )
        sender = f"From: {sender.strip()}\n" if sender else ""
        subject = f"Subject: {subject.strip()}\n" if subject else ""

        if self.method == "none":
            return label + sender + subject + body

        if self.method == "content" or self.method == "content-end":
            if self.tokenizer is None:
                # approximate token count
                n_sender = len(sender) * self.tokens_per_chr
                n_subject = len(subject) * self.tokens_per_chr
                n_body = len(body) * self.tokens_per_chr
                n_label = len(label) * self.tokens_per_chr
            else:
                # compute exact token count
                sender, subject, body, label = self.tokenizer.encode_batch(
                    [sender, subject, body, label], disallowed_special=()
                )
                n_sender = len(sender)
                n_subject = len(subject)
                n_body = len(body)
                n_label = len(label)

            if self.method == "content":
                # include label, sender, and subject if they fit
                if n_body + n_label > self.max_tokens:
                    email = body
                elif n_body + n_label + n_sender > self.max_tokens:
                    email = label + body
                elif n_body + n_label + n_sender + n_subject > self.max_tokens:
                    email = label + sender + body
                else:
                    email = label + sender + subject + body
                return email if self.tokenizer is None else self.tokenizer.decode(email)

            else:  # self.method == "content-end"
                # include label, sender and subject if they mostly fit
                if n_body > self.max_tokens:
                    email = body
                if n_body + n_label > self.max_tokens:
                    email = label + body
                elif n_body + n_label + n_sender > self.max_tokens:
                    email = label + sender + body
                else:
                    email = label + sender + subject + body

        else:  # self.method == "end":
            email = label + sender + subject + body
            if self.tokenizer is not None:
                email = self.tokenizer.encode(email, disallowed_special=())

        # self.method == "content-end" or "end", truncate from end
        if self.tokenizer is None:
            # email is str, truncate using approximate token count
            return email[: int(self.max_tokens // self.tokens_per_chr)]
        else:
            # email is a list of tokens, truncate to exact count
            return self.tokenizer.decode(email[: self.max_tokens])

    def anonymize(self, emails: Emails) -> Emails:
        """Mask sensitive data from each email.

        Args:
            emails (Emails): Emails to anonymize.

        Returns:
            Emails: The anonymized emails.
        """
        # TODO:
        return emails
