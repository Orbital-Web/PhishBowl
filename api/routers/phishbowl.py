import cv2
import numpy as np
from fastapi import APIRouter, HTTPException, Request, UploadFile
from pydantic import ValidationError
from schemas import Email, EmailDocument, EmailLabel, LabeledEmail
from services.imageprocessing import EmailImageProcessor
from services.phishbowl import PhishBowl

router = APIRouter()


# ---------------------------- COUNT ---------------------------- #


@router.get("/count")
async def count(request: Request) -> int:
    """Counts the number of emails in the phishbowl.

    Args:
        request (Request): The request object.

    Returns:
        int: Number of emails in the phishbowl.
    """
    phishbowl: PhishBowl = request.app.phishbowl

    return await phishbowl.count()


@router.post("/count_where")
async def count_where(request: Request, where: dict) -> int:
    """Counts emails in the phishbowl satisfying the metadata filter.

    Args:
        request (Request): The request object.
        where (dict): Metadata filter for emails to count.

    Returns:
        int: Number of matches.
    """
    phishbowl: PhishBowl = request.app.phishbowl

    return await phishbowl.count(where=where)


# ---------------------------- GET ---------------------------- #


@router.get("/get")
async def get(request: Request, limit: int = 0) -> list[EmailDocument]:
    """Retrieves all emails in the phishbowl.

    Args:
        request (Request): The request object.
        limit (int, optional): The maximum number of emails to retrieve. Defaults to 0
            or retrieve all.

    Returns:
        list[EmailDocument]: List of retrieved emails.
    """
    phishbowl: PhishBowl = request.app.phishbowl

    return await phishbowl.get(limit=limit)


@router.post("/get_where")
async def get_where(
    request: Request, where: dict, limit: int = 0
) -> list[EmailDocument]:
    """Retrieves all emails in the phishbowl satisfying the metadata filter.

    Args:
        request (Request): The request object.
        where (dict): Metadata filter for emails to retrieve.
        limit (int, optional): The maximum number of emails to retrieve. Defaults to 0
            or retrieve all.

    Returns:
        list[EmailDocument]: List of retrieved emails.
    """
    phishbowl: PhishBowl = request.app.phishbowl

    return await phishbowl.get(where=where, limit=limit)


@router.post("/get_similar")
async def get_similar(
    request: Request, email: Email, count: int = 10
) -> list[EmailDocument]:
    """Finds the first `count` emails in the phishbowl semantically similar to the input
    email.

    Args:
        request (Request): The request object.
        email (Email): The reference email.
        count (int, optional): Number of results to return. Defaults to 10.

    Returns:
        list[EmailDocument]: List of retrieved emails.
    """
    phishbowl: PhishBowl = request.app.phishbowl

    return await phishbowl.get_similar(email, count)


# ---------------------------- ADD ---------------------------- #


@router.post("/add_one")
async def add_one(request: Request, email: LabeledEmail, anonymize: bool = False):
    """Adds the labeled email to the phishbowl.

    Args:
        request (Request): The request object.
        email (LabeledEmail): Labeled email to add.
        anonymize (bool, optional): Whether to anonymize the email content. Defaults to
            False.
    """
    phishbowl: PhishBowl = request.app.phishbowl

    repacked_emails = {
        "sender": [email.sender],
        "subject": [email.subject],
        "body": [email.body],
        "label": [email.label],
    }
    return await phishbowl.add_emails(repacked_emails, anonymize)


@router.post("/add_many")
async def add_many(
    request: Request, emails: list[LabeledEmail], anonymize: bool = False
):
    """Adds the labeled emails to the phishbowl.

    Args:
        request (Request): The request object.
        emails (list[LabeledEmail]): List of labeled emails to add.
        anonymize (bool, optional): Whether to anonymize the email content. Defaults to
            False.
    """
    phishbowl: PhishBowl = request.app.phishbowl

    repacked_emails = {"sender": [], "subject": [], "body": [], "label": []}
    for email in emails:
        repacked_emails["sender"].append(email.sender)
        repacked_emails["subject"].append(email.subject)
        repacked_emails["body"].append(email.body)
        repacked_emails["label"].append(email.label)
    return await phishbowl.add_emails(repacked_emails, anonymize)


@router.post("/add_image")
async def add_image(
    request: Request,
    file: UploadFile,
    label: float,
    anonymize: bool = False,
):
    """Adds a labeled email image to the phishbowl.

    Args:
        request (Request): The request object.
        file (UploadFile): Image file containing the screenshot of an email to add.
        label (float): The label of the image between 0 and 1, inclusive.
        anonymize (bool, optional): Whether to anonymize the email content. Defaults to
            False.
    """
    phishbowl: PhishBowl = request.app.phishbowl
    image_processor: EmailImageProcessor = request.app.image_processor

    # ensure label is within 0 and 1
    try:
        EmailLabel.model_validate({"label": label})
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    # ensure input is an image file
    if file.content_type not in ["image/jpeg", "image/png", "image/tiff"]:
        raise HTTPException(status_code=415, detail="Invalid image file type")

    # convert image to email
    contents = await file.read()
    image = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_GRAYSCALE)
    emails = image_processor.process(image)
    emails["label"] = [label]

    return await phishbowl.add_emails(emails, anonymize)


# ---------------------------- DELETE ---------------------------- #


@router.delete("/clear")
async def clear(request: Request):
    """Deletes all emails from the phishbowl.

    Args:
        request (Request): The request object.
    """
    phishbowl: PhishBowl = request.app.phishbowl

    return await phishbowl.clear()


@router.delete("/delete_one")
async def delete_one(request: Request, email: LabeledEmail, anonymize: bool = False):
    """Deletes the labeled email from the phishbowl.

    Args:
        request (Request): The request object.
        email (LabeledEmail): Labeled email to delete.
        anonymize (bool, optional): Whether the email content was anonymized when added.
            Defaults to False.
    """
    phishbowl: PhishBowl = request.app.phishbowl

    repacked_emails = {
        "sender": [email.sender],
        "subject": [email.subject],
        "body": [email.body],
        "label": [email.label],
    }
    return await phishbowl.delete_emails(repacked_emails, anonymize)


@router.delete("/delete_many")
async def delete_many(
    request: Request, emails: list[LabeledEmail], anonymize: bool = False
):
    """Deletes the labeled emails from the phishbowl.

    Args:
        request (Request): The request object.
        emails (list[LabeledEmail]): List of labeled emails to delete.
        anonymize (bool, optional): Whether the email content was anonymized when added.
            Defaults to False.
    """
    phishbowl: PhishBowl = request.app.phishbowl

    repacked_emails = {"sender": [], "subject": [], "body": [], "label": []}
    for email in emails:
        repacked_emails["sender"].append(email.sender)
        repacked_emails["subject"].append(email.subject)
        repacked_emails["body"].append(email.body)
        repacked_emails["label"].append(email.label)
    return await phishbowl.delete_emails(repacked_emails, anonymize)


@router.delete("/delete_image")
async def delete_image(
    request: Request,
    file: UploadFile,
    label: float,
    anonymize: bool = False,
):
    """Deletes the labeled email image from the phishbowl.

    Args:
        request (Request): The request object.
        file (UploadFile): Image file containing the screenshot of an email to delete.
        label (float): The label of the image between 0 and 1, inclusive.
        anonymize (bool, optional): Whether the email content was anonymized when added.
            Defaults to False.
    """
    phishbowl: PhishBowl = request.app.phishbowl
    image_processor: EmailImageProcessor = request.app.image_processor

    # ensure label is within 0 and 1
    try:
        EmailLabel.model_validate({"label": label})
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    # ensure input is an image file
    if file.content_type not in ["image/jpeg", "image/png", "image/tiff"]:
        raise HTTPException(status_code=415, detail="Invalid image file type")

    # convert image to email
    contents = await file.read()
    image = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_GRAYSCALE)
    emails = image_processor.process(image)
    emails["label"] = [label]

    return await phishbowl.delete_emails(emails, anonymize)
