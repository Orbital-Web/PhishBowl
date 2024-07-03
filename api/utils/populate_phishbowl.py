from services.phishbowl import load_phishbowl
import asyncio


def populate_phishbowl():
    phishbowl = asyncio.run(load_phishbowl())
    # TODO:
