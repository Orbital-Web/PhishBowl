from fastapi import FastAPI, UploadFile, HTTPException
from contextlib import asynccontextmanager
from schemas import Email, AnalysisResponse
from models import Emails
from services.phishbowl import load_phishbowl
from services.phishnets import EnsemblePhishNet
from services.imageprocessing import EmailImageProcessor
from services.textprocessing import EmailTextProcessor
import numpy as np
import cv2


@asynccontextmanager
async def lifespan(app: FastAPI):
    global phishbowl, phishnet
    # startup
    phishbowl = await load_phishbowl()
    phishnet = EnsemblePhishNet(phishbowl)
    yield
    # cleanup


app = FastAPI(lifespan=lifespan)
phishbowl = None
phishnet = None
image_processor = EmailImageProcessor()
text_processor = EmailTextProcessor()


# email analysis
@app.post("/analyze/image")
async def analyze_image(file: UploadFile, anonymize: bool = False) -> AnalysisResponse:
    """Analyzes whether the screenshot contains a phishing email.

    Args:
        file (UploadFile): Image file containing the screenshot of an email.
        anonymize (bool, optional): Whether to anonymize the email content when adding
            to the PhishBowl. Defaults to False.

    Returns:
        AnalysisResponse: Response containing the analysis result.
    """
    # ensure input is an image file
    if file.content_type not in ["image/jpeg", "image/png", "image/tiff"]:
        raise HTTPException(status_code=400, detail="Invalid image file type")

    # convert image to email text
    contents = await file.read()
    image = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_GRAYSCALE)
    email_text = await image_processor.process(image)

    # analyze
    response = await analyze_text(email_text, anonymize)
    return response


@app.post("/analyze/text")
async def analyze_text(email_text: str, anonymize: bool = False) -> AnalysisResponse:
    """Analyzes whether the email text is that of a phishing email.

    Args:
        email_text (str): Text containing the email content. May contain other junk.
        anonymize (bool, optional): Whether to anonymize the email content when adding
            to the PhishBowl. Defaults to False.

    Returns:
        AnalysisResponse: Response containing the analysis result.
    """
    emails = await text_processor.from_text(email_text)

    # anonymize if requested
    if anonymize:
        emails = await text_processor.anonymize(emails)

    # analyze
    response = await analyze_emails_batch(emails)

    # update phishbowl
    # TODO:

    return response[0]


@app.post("/analyze/email")
async def analyze_email(email: Email, anonymize: bool = False) -> AnalysisResponse:
    """Analyzes whether the email is a phishing email.

    Args:
        email (Email): The email to analyze.
        anonymize (bool, optional): Whether to anonymize the email content when adding
            to the PhishBowl. Defaults to False.

    Returns:
        AnalysisResponse: Response containing the analysis result.
    """
    emails = {
        "sender": [email.sender],
        "subject": [email.subject],
        "body": [email.body],
    }

    # analyze
    response = await analyze_emails_batch(emails)

    # update phishbowl
    # TODO:

    return response[0]


async def analyze_emails_batch(emails: Emails) -> list[AnalysisResponse]:
    """Analyzes each email in the email batch for whether it is a phishing email.

    Args:
        emails (Emails): The email batch to analyze.

    Returns:
        list[AnalysisResponse]: Analysis result for each email.
    """
    scores = await phishnet.analyze(emails)
    responses = []
    for score in scores:
        label = "PHISHING" if score >= 0.5 else "LEGITIMATE"
        confidence = min(1, 2 * abs(score - 0.5))
        responses.append(AnalysisResponse(label=label, confidence=confidence))
    return responses
