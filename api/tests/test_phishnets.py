import os

import pytest
from services.phishbowl import load_phishbowl
from services.phishnets import (
    EnsemblePhishNet,
    FineTunedBERTPhishNet,
    GPTPhishNet,
    HFBERTPhishNet,
    SemanticPhishNet,
    SenderPhishNet,
)

requires_docker = pytest.mark.skipif(
    not os.getenv("IS_DOCKER_CONTAINER", False), reason="requires docker to be running"
)
requires_azure = pytest.mark.skipif(
    "AZURE_OPENAI_API_KEY" not in os.environ
    or "AZURE_OPENAI_ENDPOINT" not in os.environ,
    reason="requires azure openai endpoint and key",
)
requires_hfread = pytest.mark.skipif(
    "HUGGINGFACE_TOKEN_READ" not in os.environ, reason="requires huggingface read token"
)
requires_hfwrite = pytest.mark.skipif(
    "HUGGINGFACE_TOKEN_WRITE" not in os.environ,
    reason="requires huggingface write token",
)


@pytest.fixture
def emails():
    return {
        "sender": [None, "Microsoft <micro@soft101.com>"],
        "subject": [None, "Your account has been compromised"],
        "body": ["Hello", "Please reset your password with this link"],
    }


@requires_docker
async def test_semantic_phishnet_analyze_runs(emails):
    phishbowl = await load_phishbowl()
    phishnet = SemanticPhishNet(phishbowl)
    results = await phishnet.analyze(emails)
    assert len(results) == 2
    for result in results:
        assert 0 <= result.get("phishing_score") <= 1
        assert 0 <= result.get("confidence") <= 1


@requires_azure
async def test_gpt_phishnet_analyze_runs(emails):
    phishnet = GPTPhishNet()
    results = await phishnet.analyze(emails)
    assert len(results) == 2
    for result in results:
        assert 0 <= result.get("phishing_score") <= 1
        assert type(result.get("impersonating")) in (None.__class__, str)
        assert isinstance(result.get("reason"), str)


@requires_docker
@requires_azure
async def test_ensemble_phishnet_analyze_runs(emails):
    phishbowl = await load_phishbowl()
    phishnet = EnsemblePhishNet(phishbowl)
    results = await phishnet.analyze(emails)
    for result in results:
        assert 0 <= result.get("phishing_score") <= 1
        assert 0 <= result.get("semantic_confidence") <= 1
        assert type(result.get("impersonating")) in (None.__class__, str)
        assert isinstance(result.get("reason"), str)


@requires_docker
@requires_hfwrite
async def test_finetunedbert_phishnet_analyze_runs(emails):
    phishnet = FineTunedBERTPhishNet()
    results = await phishnet.analyze(emails)
    assert len(results) == 2
    for result in results:
        assert 0 <= result.get("phishing_score") <= 1


@requires_hfread
async def test_hfbert_phishnet_analyze_runs(emails):
    phishnet = HFBERTPhishNet()
    results = await phishnet.analyze(emails)
    assert len(results) == 2
    for result in results:
        assert 0 <= result.get("phishing_score") <= 1


@requires_docker
@pytest.mark.skip(reason="sender phishnet is currently WIP")
async def test_sender_phishnet_analyze_runs(emails):
    phishnet = SenderPhishNet()
    results = await phishnet.analyze(emails)
    assert len(results) == 2
    for result in results:
        assert 0 <= result.get("phishing_score") <= 1
