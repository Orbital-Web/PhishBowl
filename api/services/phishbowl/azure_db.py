import os

from chromadb.utils import embedding_functions
from models import PhishBowlDB

import chromadb


class AzureDB(PhishBowlDB):
    """A PhishBowl database using azure openai embeddings."""

    collection_name = "phishbowl-azure-openai"

    async def initialize_db(self):
        self.client = await chromadb.AsyncHttpClient(host="chromadb", port=5000)
        self.collection = await self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=embedding_functions.OpenAIEmbeddingFunction(
                api_type="azure",
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_version="2024-06-01",
                model_name="text-embedding-3-small",
            ),
            metadata={"hnsw:space": "l2"},
        )
