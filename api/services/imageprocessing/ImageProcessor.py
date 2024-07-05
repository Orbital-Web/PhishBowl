import pytesseract
import numpy as np
from numpy.typing import NDArray


class EmailImageProcessor:
    """A class for extracting the text from a screenshot of an email."""

    def __init__(self):
        self.threshold = 80

    def process(self, image: NDArray[np.uint8]) -> str:
        """Extract the relevant text from an email screenshot.

        Args:
            image (NDArray[np.uint8]): Image data of the screenshot.

        Returns:
            str: Extracted text.
        """
        # get data of where the texts are on the image and their confidence
        imagedata = [
            s.split("\t") for s in pytesseract.image_to_data(image).split("\n")[1:-1]
        ]

        # extract worthwhile content and organize the text
        BLOCK_NUM, CONF, TEXT = 2, 10, 11
        previous_block = 0
        imagetexts = []
        for data in imagedata:
            if int(data[BLOCK_NUM]) != previous_block:
                previous_block = int(data[BLOCK_NUM])
                imagetexts.append("\n")
            if float(data[CONF]) >= self.threshold and data[TEXT].strip():
                imagetexts.append(data[TEXT])
        imagetext = " ".join(imagetexts)

        return imagetext
