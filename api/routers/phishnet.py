from fastapi import APIRouter, Request, UploadFile, HTTPException
from schemas import Email, AnalysisResponse
from models import Emails, PhishNet
from services.phishbowl import PhishBowl
from services.imageprocessing import EmailImageProcessor
from services.textprocessing import EmailTextProcessor
import numpy as np
import cv2


router = APIRouter()


@router.post("/image")
async def analyze_image(
    request: Request, file: UploadFile, anonymize: bool = False
) -> AnalysisResponse:
    """Analyzes whether the screenshot contains a phishing email and adds suspicious
    emails to the phishbowl.

    Args:
        request (Request): The request object.
        file (UploadFile): Image file containing the screenshot of an email.
        anonymize (bool, optional): Whether to anonymize the email content when adding
            to the phishbowl. Defaults to False.

    Returns:
        AnalysisResponse: Response containing the analysis result.
    """
    image_processor: EmailImageProcessor = request.app.image_processor

    # ensure input is an image file
    if file.content_type not in ["image/jpeg", "image/png", "image/tiff"]:
        raise HTTPException(status_code=400, detail="Invalid image file type")

    # convert image to email text
    contents = await file.read()
    image = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_GRAYSCALE)
    email_text = image_processor.process(image)

    # analyze
    response = await analyze_text(request, email_text, anonymize)
    return response


@router.post("/text")
async def analyze_text(
    request: Request, email_text: str, anonymize: bool = False
) -> AnalysisResponse:
    """Analyzes whether the email text is that of a phishing email and adds
    suspicious emails to the phishbowl.

    Args:
        request (Request): The request object.
        email_text (str): Text containing the email content. May contain other junk.
        anonymize (bool, optional): Whether to anonymize the email content when adding
            to the phishbowl. Defaults to False.

    Returns:
        AnalysisResponse: Response containing the analysis result.
    """
    phishnet: PhishNet = request.app.phishnet
    phishbowl: PhishBowl = request.app.phishbowl
    text_processor: EmailTextProcessor = request.app.text_processor

    emails = text_processor.from_text(email_text)
    response = await analyze_emails_batch(phishnet, emails)

    # add to phishbowl if TODO:
    if False:
        # anonymize if requested
        if anonymize:
            emails = text_processor.anonymize(emails)
        await phishbowl.add_emails(emails)

    return response[0]


@router.post("/email")
async def analyze_email(
    request: Request, email: Email, anonymize: bool = False
) -> AnalysisResponse:
    """Analyzes whether the email is a phishing email and adds suspicious emails to the
    phishbowl.

    Args:
        request (Request): The request object.
        email (Email): The email to analyze.
        anonymize (bool, optional): Whether to anonymize the email content when adding
            to the phishbowl. Defaults to False.

    Returns:
        AnalysisResponse: Response containing the analysis result.
    """
    phishnet: PhishNet = request.app.phishnet
    phishbowl: PhishBowl = request.app.phishbowl
    text_processor: EmailTextProcessor = request.app.text_processor

    emails = {
        "sender": [email.sender],
        "subject": [email.subject],
        "body": [email.body],
    }
    response = await analyze_emails_batch(phishnet, emails)

    # add to phishbowl if TODO:
    if False:
        # anonymize if requested
        if anonymize:
            emails = text_processor.anonymize(emails)
        await phishbowl.add_emails(emails)

    return response[0]


async def analyze_emails_batch(
    phishnet: PhishNet, emails: Emails
) -> list[AnalysisResponse]:
    """Analyzes each email in the email batch for whether it is a phishing email.

    Args:
        phishnet (PhishNet): PhishNet to use for analyzis.
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
