import os

import pytest

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
skip_wip = pytest.mark.skip(reason="currently WIP")
