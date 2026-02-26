from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ['API_KEY'] = 'test-key'

from services.ledger_service.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_entry_unauthorized():
    response = client.post("/entries", json={
        "payment_id": "pay_1",
        "sender_account": "ACC001",
        "receiver_account": "ACC002",
        "amount": 100.0,
        "currency": "USD",
        "reference": "TEST001"
    })
    assert response.status_code == 401

def test_get_entries_unauthorized():
    response = client.get("/entries/pay_1")
    assert response.status_code == 401
