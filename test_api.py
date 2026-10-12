from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "LegalEase API is running"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_generate_fallback(monkeypatch):
    from backend import routes
    monkeypatch.setattr(routes._generator, "api_key", "")
    response = client.post("/generate", json={
        "document_type": "Non-Disclosure Agreement",
        "parties": "Alice (Disclosing Party), Acme Ltd (Receiving Party)",
        "terms": "Keep information confidential; no disclosure to third parties",
        "effective_date": "2026-10-06",
        "jurisdiction": "Tamil Nadu, India",
    })
    assert response.status_code == 200
    body = response.json()
    assert body["fallback"] is True
    assert "NON-DISCLOSURE AGREEMENT" in body["content"]


def test_validation_rejects_empty_parties():
    response = client.post("/generate", json={
        "document_type": "NDA",
        "parties": "",
        "terms": "Confidentiality",
        "effective_date": "2026-10-06",
    })
    assert response.status_code == 422
