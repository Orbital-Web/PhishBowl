from typing import Literal

import tiktoken
from models import Emails


class EmailTextProcessor:
    """A class for processing and truncating emails."""

    def __init__(
        self,
        max_tokens: int = 512,
        truncate_method: Literal["none", "content", "end"] = "none",
        tokenizer_model: None | str = None,
    ):
        self.max_tokens = max_tokens
        self.method: Literal["none", "content", "end"] = truncate_method
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
        documents = [
            self.truncate(sender, subject, body)
            for sender, subject, body in zip(
                emails["sender"], emails["subject"], emails["body"]
            )
        ]
        return documents

    def truncate(self, sender: str | None, subject: str | None, body: str) -> str:
        """Truncates the email content string to be below self.max_tokens.
        Truncation strategy depends on self.method and self.tokenizer.
        Method:
            - none: no truncation, tokenizer is ignored
            - content: always keep whole body, include sender and subject if they fit
            - end: truncate from the end
        Tokenizer:
            - None: estimate token count based on string length
            - Encoding: use a particular tokenizer to get the exact token count

        Args:
            sender (str | None): email sender info
            subject (str | None): email subject line
            body (str): email body

        Returns:
            str: The truncated email string
        """
        sender = f"From: {sender.strip()}\n" if sender else ""
        subject = f"Subject: {subject.strip()}\n" if subject else ""

        if self.method == "none":
            return sender + subject + body

        if self.method == "content":
            # count tokens
            if self.tokenizer is None:
                t_sender = len(sender) * self.tokens_per_chr
                t_subject = len(subject) * self.tokens_per_chr
                t_body = len(body) * self.tokens_per_chr
            else:
                t_sender, t_subject, t_body = self.tokenizer.encode_batch(
                    [sender, subject, body]
                )
                t_sender = len(t_sender)
                t_subject = len(t_subject)
                t_body = len(t_body)

            # include subject and sender if they fit
            if t_body + t_sender > self.max_tokens:
                return body
            elif t_body + t_sender + t_subject > self.max_tokens:
                return sender + body
            else:
                return sender + subject + body

        # truncate from end
        emailtext = sender + subject + body
        if self.tokenizer is None:
            t_truncate = len(emailtext) * self.tokens_per_chr - self.max_tokens
            if t_truncate <= 0:
                return emailtext
            else:
                return emailtext[: -int(t_truncate // self.max_tokens)]
        else:
            tokens = self.tokenizer.encode(emailtext)
            return self.tokenizer.decode(tokens[: self.max_tokens])

    def anonymize(self, emails: Emails) -> Emails:
        """Mask sensitive data from each email.

        Args:
            emails (Emails): Emails to anonymize.

        Returns:
            Emails: The anonymized emails.
        """
        # TODO:
        return emails
