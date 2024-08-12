from models import PhishBowlDB

import chromadb
from chromadb.utils import embedding_functions


class SentenceTransformerDB(PhishBowlDB):
    """A PhishBowl database using sentence transformers embeddings."""

    collection_name = "phishbowl"

    def __init__(self, model_name: str = "avsolatorio/GIST-small-Embedding-v0"):
        super().__init__()
        self.model_name = model_name

    async def initialize_db(self):
        self.client = await chromadb.AsyncHttpClient(host="chromadb", port=5000)
        self.collection = await self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.model_name
            ),
            metadata={"hnsw:space": "l2"},
        )
