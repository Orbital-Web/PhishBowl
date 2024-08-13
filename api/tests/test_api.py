import pytest
from fastapi.testclient import TestClient
from routers import app
from services.phishbowl import PhishBowl
from tests.decorators import requires_azure, requires_docker, skip_wip


@requires_docker
@requires_azure
class TestPhishBowlAPI:
    @pytest.fixture(autouse=True)
    def setup_method(self, monkeypatch):
        async def mock_load_phishbowl():
            phishbowl = PhishBowl()
            phishbowl.db.collection_name = "phishbowl-test"
            await phishbowl.db.initialize_db()
            return phishbowl

        monkeypatch.setattr("routers.load_phishbowl", mock_load_phishbowl)
        self.client = TestClient(app)
        self.client.__enter__()

    def teardown_method(self):
        self.client.delete("/phishbowl/clear")
        self.client.__exit__()

    def test_count_should_return_0_if_phishbowl_empty(self):
        response = self.client.get("/phishbowl/count")
        assert response.status_code == 200
        assert response.json() == 0

    def test_count_where(self):
        response = self.client.post(
            "/phishbowl/add_one/?anonymize=false",
            json={
                "sender": "name",
                "subject": "hi",
                "body": "hello",
                "label": 1.0,
            },
        )
        assert response.status_code == 200

        response = self.client.post(
            "/phishbowl/count_where", json={"label": {"$gte": 0.5}}
        )
        assert response.status_code == 200
        assert response.json() == 1

        response = self.client.post(
            "/phishbowl/count_where", json={"label": {"$lt": 0.5}}
        )
        assert response.status_code == 200
        assert response.json() == 0

    def test_add_and_delete_one(self):
        response = self.client.post(
            "/phishbowl/add_one/?anonymize=false",
            json={
                "sender": "name",
                "subject": "hi",
                "body": "hello",
                "label": 1.0,
            },
        )
        assert response.status_code == 200

        response = self.client.get("/phishbowl/count")
        assert response.status_code == 200
        assert response.json() == 1

        response = self.client.request(
            "DELETE",
            "/phishbowl/delete_one/?anonymize=false",
            json={
                "sender": "name",
                "subject": "hi",
                "body": "hello",
                "label": 1.0,
            },
        )
        assert response.status_code == 200

        response = self.client.get("/phishbowl/count")
        assert response.status_code == 200
        assert response.json() == 0

    def test_add_one_with_duplicate_should_do_nothing(self):
        for _ in range(2):
            response = self.client.post(
                "/phishbowl/add_one/?anonymize=false",
                json={
                    "sender": "name",
                    "subject": "hi",
                    "body": "hello",
                    "label": 1.0,
                },
            )
            assert response.status_code == 200

        response = self.client.get("/phishbowl/count")
        assert response.status_code == 200
        assert response.json() == 1

    def test_add_and_delete_many(self):
        response = self.client.post(
            "/phishbowl/add_many/?anonymize=false",
            json=[
                {
                    "sender": "name",
                    "subject": "hi",
                    "body": "hello",
                    "label": 1.0,
                },
                {
                    "sender": "name",
                    "subject": "different",
                    "body": "bye",
                    "label": 0.0,
                },
            ],
        )
        assert response.status_code == 200

        response = self.client.get("/phishbowl/count")
        assert response.status_code == 200
        assert response.json() == 2

        response = self.client.request(
            "DELETE",
            "/phishbowl/delete_many/?anonymize=false",
            json=[
                {
                    "sender": "name",
                    "subject": "hi",
                    "body": "hello",
                    "label": 1.0,
                },
                {
                    "sender": "name",
                    "subject": "different",
                    "body": "bye",
                    "label": 0.0,
                },
            ],
        )
        assert response.status_code == 200

        response = self.client.get("/phishbowl/count")
        assert response.status_code == 200
        assert response.json() == 0

    def test_add_and_delete_image(self):
        with open("/app/tests/fixtures/email_screenshot.jpg", "rb") as f:
            response = self.client.post(
                "/phishbowl/add_image/?label=1&anonymize=false",
                files={"file": f},
            )
            assert response.status_code == 200

        response = self.client.get("/phishbowl/count")
        assert response.status_code == 200
        assert response.json() == 1

        with open("/app/tests/fixtures/email_screenshot.jpg", "rb") as f:
            response = self.client.request(
                "DELETE",
                "/phishbowl/delete_image/?label=1&anonymize=false",
                files={"file": f},
            )
            assert response.status_code == 200

        response = self.client.get("/phishbowl/count")
        assert response.status_code == 200
        assert response.json() == 0

    def test_clear(self):
        response = self.client.post(
            "/phishbowl/add_one/?anonymize=false",
            json={
                "sender": "name",
                "subject": "hi",
                "body": "hello",
                "label": 1.0,
            },
        )
        assert response.status_code == 200

        response = self.client.delete("/phishbowl/clear")
        assert response.status_code == 200

        response = self.client.get("/phishbowl/count")
        assert response.status_code == 200
        assert response.json() == 0

    def test_add_and_delete_one_with_anonymize(self):
        response = self.client.post(
            "/phishbowl/add_one/?anonymize=true",
            json={
                "sender": "name",
                "subject": "hi",
                "body": "hello",
                "label": 1.0,
            },
        )
        assert response.status_code == 200

        response = self.client.get("/phishbowl/count")
        assert response.status_code == 200
        assert response.json() == 1

        response = self.client.request(
            "DELETE",
            "/phishbowl/delete_one/?anonymize=true",
            json={
                "sender": "name",
                "subject": "hi",
                "body": "hello",
                "label": 1.0,
            },
        )
        assert response.status_code == 200

        response = self.client.get("/phishbowl/count")
        assert response.status_code == 200
        assert response.json() == 0

    def test_add_and_delete_many_with_anonymize(self):
        response = self.client.post(
            "/phishbowl/add_many/?anonymize=true",
            json=[
                {
                    "sender": "name",
                    "subject": "hi",
                    "body": "hello",
                    "label": 1.0,
                },
                {
                    "sender": "name",
                    "subject": "different",
                    "body": "bye",
                    "label": 0.0,
                },
            ],
        )
        assert response.status_code == 200

        response = self.client.get("/phishbowl/count")
        assert response.status_code == 200
        assert response.json() == 2

        response = self.client.request(
            "DELETE",
            "/phishbowl/delete_many/?anonymize=true",
            json=[
                {
                    "sender": "name",
                    "subject": "hi",
                    "body": "hello",
                    "label": 1.0,
                },
                {
                    "sender": "name",
                    "subject": "different",
                    "body": "bye",
                    "label": 0.0,
                },
            ],
        )
        assert response.status_code == 200

        response = self.client.get("/phishbowl/count")
        assert response.status_code == 200
        assert response.json() == 0

    def test_add_and_delete_image_with_anonymize(self):
        with open("/app/tests/fixtures/email_screenshot.jpg", "rb") as f:
            response = self.client.post(
                "/phishbowl/add_image/?label=0&anonymize=true",
                files={"file": f},
            )
            assert response.status_code == 200

        response = self.client.get("/phishbowl/count")
        assert response.status_code == 200
        assert response.json() == 1

        with open("/app/tests/fixtures/email_screenshot.jpg", "rb") as f:
            response = self.client.request(
                "DELETE",
                "/phishbowl/delete_image/?label=0&anonymize=true",
                files={"file": f},
            )
            assert response.status_code == 200

        response = self.client.get("/phishbowl/count")
        assert response.status_code == 200
        assert response.json() == 0


@requires_docker
@requires_azure
@skip_wip
class TestPhishNetAPI:
    @pytest.fixture(autouse=True)
    def setup_method(self, monkeypatch):
        async def mock_load_phishbowl():
            phishbowl = PhishBowl()
            phishbowl.db.collection_name = "phishbowl-test"
            await phishbowl.db.initialize_db()
            return phishbowl

        monkeypatch.setattr("routers.load_phishbowl", mock_load_phishbowl)
        self.client = TestClient(app)
        self.client.__enter__()

    def teardown_method(self):
        self.client.delete("/phishbowl/clear")
        self.client.__exit__()
