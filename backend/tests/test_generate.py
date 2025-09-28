import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_generate_endpoint():
    test_file = "frontend/static/sample1.jpg"
    assert os.path.exists(test_file), "Sample image not found!"

    with open(test_file, "rb") as f:
        response = client.post(
            "/api/generate",
            data={"product_id": "test123", "style": "modern"},
            files={"file": ("sample1.jpg", f, "image/jpeg")},
        )

    assert response.status_code == 200
    assert isinstance(response.json(), str) or "job_id" in response.text
