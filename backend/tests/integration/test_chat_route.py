from fastapi.testclient import TestClient

from backend.app.main import create_app


class FakePipeline:
    def chat(self, messages):
        return {
            "raw_emotion": "fear",
            "emotion": "anxiety",
            "strategy": "reassure_and_structure",
            "response": "It sounds like you're carrying a lot right now. What feels most uncertain?",
        }


def fake_loader(app):
    app.state.ready = True
    app.state.chat_pipeline = FakePipeline()


def test_healthz_returns_ok():
    with TestClient(create_app(startup_loader=fake_loader)) as client:
        response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_returns_structured_response():
    with TestClient(create_app(startup_loader=fake_loader)) as client:
        response = client.post("/chat", json={"messages": [{"role": "user", "content": "I feel worried"}]})
    assert response.status_code == 200
    assert response.json()["emotion"] == "anxiety"


def test_chat_rejects_invalid_payload():
    with TestClient(create_app(startup_loader=fake_loader)) as client:
        response = client.post("/chat", json={"messages": []})
    assert response.status_code == 422
