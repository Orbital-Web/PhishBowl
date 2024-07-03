from fastapi import APIRouter, Request
from schemas import Email, LabeledEmail
from services.phishbowl import PhishBowl

router = APIRouter()


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
        request (Request): The request object
        where (dict): Metadata filter for emails to count.

    Returns:
        int: Number of matches.
    """
    phishbowl: PhishBowl = request.app.phishbowl

    return await phishbowl.count(where=where)


@router.post("/add_one")
async def add_one(request: Request, email: LabeledEmail):
    """Adds the labeled email to the phishbowl.

    Args:
        request (Request): The request object.
        email (LabeledEmail): Labeled email to add.
    """
    phishbowl: PhishBowl = request.app.phishbowl

    repacked_emails = {
        "sender": [email.sender],
        "subject": [email.subject],
        "body": [email.body],
        "label": [email.label],
    }
    return await phishbowl.add_emails(repacked_emails)


@router.post("/add_many")
async def add_many(request: Request, emails: list[LabeledEmail]):
    """Adds the labeled emails to the phishbowl.

    Args:
        request (Request): The request object.
        emails (list[LabeledEmail]): List of labeled emails to add.
    """
    phishbowl: PhishBowl = request.app.phishbowl

    repacked_emails = {"sender": [], "subject": [], "body": [], "label": []}
    for email in emails:
        repacked_emails["sender"].append(email.sender)
        repacked_emails["subject"].append(email.subject)
        repacked_emails["body"].append(email.body)
        repacked_emails["label"].append(email.label)
    return await phishbowl.add_emails(repacked_emails)


@router.delete("/clear")
async def clear(request: Request):
    """Deletes all emails from the phishbowl.

    Args:
        request (Request): The request object.
    """
    phishbowl: PhishBowl = request.app.phishbowl

    return await phishbowl.clear()


@router.delete("/delete_one")
async def delete_one(request: Request, email: Email):
    """Deletes the email from the phishbowl.

    Args:
        request (Request): The request object.
        email (Email): Email to delete.
    """
    phishbowl: PhishBowl = request.app.phishbowl

    repacked_emails = {
        "sender": [email.sender],
        "subject": [email.subject],
        "body": [email.body],
    }
    return await phishbowl.delete_emails(repacked_emails)


@router.delete("/delete_many")
async def delete_many(request: Request, emails: list[Email]):
    """Deletes the emails from the phishbowl.

    Args:
        request (Request): The request object.
        emails (list[Email]): List of emails to delete.
    """
    phishbowl: PhishBowl = request.app.phishbowl

    repacked_emails = {"sender": [], "subject": [], "body": []}
    for email in emails:
        repacked_emails["sender"].append(email.sender)
        repacked_emails["subject"].append(email.subject)
        repacked_emails["body"].append(email.body)
    return await phishbowl.delete_emails(repacked_emails)
