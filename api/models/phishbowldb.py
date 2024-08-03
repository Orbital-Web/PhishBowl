from abc import ABCMeta, abstractmethod

from chromadb.api import AsyncClientAPI
from chromadb.api.models.AsyncCollection import AsyncCollection


class PhishBowlDB(metaclass=ABCMeta):
    """A base class for the PhishBowl database backend."""

    collection_name: str

    def __init__(self):
        self.client: AsyncClientAPI
        self.collection: AsyncCollection

    @abstractmethod
    async def initialize_db(self):
        """Initializes the client and collection with a custom embedding function."""
        pass

    async def clear(self):
        """Removes all documents in the collection."""
        await self.client.delete_collection(self.collection_name)
        await self.initialize_db()
