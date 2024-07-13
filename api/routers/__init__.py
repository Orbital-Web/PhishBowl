from contextlib import asynccontextmanager

from fastapi import FastAPI
from routers.phishbowl import router as phishbowl_router
from routers.phishnet import router as phishnet_router
from services.imageprocessing import EmailImageProcessor
from services.phishbowl import load_phishbowl
from services.phishnets import EnsemblePhishNet
from services.textprocessing import EmailTextProcessor

tags = [
    {"name": "PhishBowl", "description": "Endpoints for operation on the PhishBowl"},
    {"name": "PhishNet", "description": "Endpoints for email analysis"},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    app.phishbowl = await load_phishbowl()
    app.phishnet = EnsemblePhishNet(app.phishbowl)
    app.image_processor = EmailImageProcessor()
    app.text_processor = EmailTextProcessor()
    yield
    # shutdown


app = FastAPI(lifespan=lifespan, openapi_tags=tags)
app.include_router(phishbowl_router, prefix="/phishbowl", tags=["PhishBowl"])
app.include_router(phishnet_router, prefix="/analyze", tags=["PhishNet"])
