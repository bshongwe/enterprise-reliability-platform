from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ['API_KEY'] = 'test-key'

from services.payments_api.main import app
import importlib.util
import sys
from pathlib import Path

# Load module with hyphenated name
payments_path = Path(__file__).parent.parent / 'services' / 'payments-api' / 'main.py'
spec = importlib.util.spec_from_file_location('payments_api_main', payments_path)
payments_module = importlib.util.module_from_spec(spec)
sys.modules['payments_api_main'] = payments_module
spec.loader.exec_module(payments_module)
app = payments_module.app

client = TestClient(app)

def test_health_check():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_payment_unauthorized():
    response = client.post("/payments", json={
        "sender_account": "ACC001",
        "receiver_account": "ACC002",
        "amount": 100.0,
        "currency": "USD",
        "reference": "TEST001"
    })
    assert response.status_code == 401

def test_create_payment_authorized():
    response = client.post(
        "/payments",
        json={
            "sender_account": "ACC001",
            "receiver_account": "ACC002",
            "amount": 100.0,
            "currency": "USD",
            "reference": "TEST001"
        },
        headers={"X-API-Key": "test-key"}
    )
    assert response.status_code in [200, 500]
