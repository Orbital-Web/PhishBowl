import logging

import numpy as np
import pytesseract
from models import Emails
from numpy.typing import NDArray
from pandas import DataFrame

logger = logging.getLogger(__name__)


class EmailImageProcessor:
    """A class for extracting the text from a screenshot of an email."""

    def __init__(self):
        self.threshold = 80  # minimum confidence to count as text
        self.header_scale = 1.25  # scale factor of subject size to body size
        self.logo_scale = 2  # scale factor of logo and other junk to body size
        self.header_until = 7  # line number until we stop considering as the header
        self.header_words = [
            "from",
            "to",
            "subject",
            "cc",
            "bcc",
            "sent",
            "tome",
            "sender",
        ]  # common words found in the header
        self.starter_words = [
            "hi",
            "hello",
            "dear",
            "thank",
            "thanks",
        ]  # common words found at the start of the body
        self.unsafe_patterns = [
            "content in this message has been blocked",
            "caution: this is an external email",
        ]  # patterns of caution message for unsafe emails

    def process(self, image: NDArray[np.uint8]) -> Emails:
        """Extract the relevant content from an email screenshot.

        Args:
            image (NDArray[np.uint8]): Image data of the screenshot.

        Returns:
            Emails: Extracted email content.
        """
        # extract text from image
        content: DataFrame = pytesseract.image_to_data(image, output_type="data.frame")
        content = content[content["conf"] > self.threshold]

        # get text sizes
        median_size = content["height"].median()
        header_size = self.header_scale * median_size
        logo_size = self.logo_scale * median_size

        # group by lines
        content = (
            content.groupby(["block_num", "par_num", "line_num"])
            .agg({"height": "mean", "text": " ".join})
            .reset_index()
        )

        # find rows that starts with or equals common header and starter words
        pattern = r"|".join(self.header_words)
        header_rows = content[
            content["text"].str.match(f"^({pattern})([: ]|$)", case=False, na=False)
            & (content.index < self.header_until)
        ]
        pattern = r"|".join(self.starter_words)
        starter_rows = content[
            content["text"].str.match(f"^({pattern})([: ]|$)", case=False, na=False)
        ]

        # seperate content into header and body
        header_until = (
            self.header_until if header_rows.empty else header_rows.index[-1] + 1
        )
        body_from = (
            0 if starter_rows.empty else min(header_until, starter_rows.index[0])
        )
        header = content[:header_until]
        body = content[body_from:]

        # get sender from header, either directly or use the text above "to" / "tome"
        sender_rows = header["text"].str.extract(r"(?i)^\bfrom[: ]\s*(.*)").dropna()
        sender = sender_rows.iloc[0, 0] if not sender_rows.empty else ""
        if not sender:
            to_rows = header[
                header["text"].str.match(r"^to(me)?([: ]|$)", case=False, na=False)
            ]
            if not to_rows.empty and to_rows.index[0] > 0:
                sender = header["text"][to_rows.index[0] - 1]

        # get subject from header either directly or through font size comparisons
        subject_rows = header["text"].str.extract(r"(?i)^\bsubject[: ]\s*(.*)").dropna()
        subject = subject_rows.iloc[0, 0] if not subject_rows.empty else ""
        if not subject:
            subject_rows = header[
                header["height"].between(header_size, logo_size, inclusive="left")
            ]
            subject = " ".join(subject_rows["text"])

        # get other useful information
        unsafe = (
            content["text"]
            .str.contains("|".join(self.unsafe_patterns), case=False, na=False)
            .any()
        )

        # convert to email
        body.loc[body["text"].str.strip() == "", "text"] = "\n"
        emails: Emails = {
            "sender": [sender],
            "subject": [subject],
            "body": [body["text"].str.cat(sep=" ")],
            "unsafe": [unsafe],
        }
        logger.info(emails)
        return emails
