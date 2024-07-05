from services.phishbowl import load_phishbowl
from services.data import load_emails
import asyncio
import logging

logger = logging.getLogger(__name__)


def populate_phishbowl(reset: bool):
    """Populates the phishbowl with the training dataset. If stopped and ran again, it
    will continue loading the remaining emails in the dataset.

    Args:
        reset (bool): Whether to reset the phishbowl before populating it.
    """
    logger.info("Loading phishbowl...")
    phishbowl = asyncio.run(load_phishbowl())
    traindata = load_emails(shuffle=False)

    # reset phishbowl
    if reset:
        logger.info("Reseting phishbowl...")
        asyncio.run(phishbowl.clear())

    # continue loading from where we last left off
    logger.info("Populating phishbowl...")
    start_index = asyncio.run(phishbowl.count())

    dataset = traindata.datasetdict["train"].skip(start_index)
    asyncio.run(phishbowl.add_dataset(dataset))

    logger.info("Completed populating the phishbowl")
