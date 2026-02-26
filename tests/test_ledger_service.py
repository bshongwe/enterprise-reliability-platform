from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ['API_KEY'] = 'test-key'

import importlib.util
from pathlib import Path

# Add ledger-service directory to path for relative imports
ledger_dir = Path(__file__).parent.parent / 'services' / 'ledger-service'
sys.path.insert(0, str(ledger_dir))

# Load module with hyphenated name
ledger_path = ledger_dir / 'main.py'
spec = importlib.util.spec_from_file_location('__main__', ledger_path, submodule_search_locations=[str(ledger_dir)])
ledger_module = importlib.util.module_from_spec(spec)
ledger_module.__package__ = ''
sys.modules['__main__'] = ledger_module
spec.loader.exec_module(ledger_module)
app = ledger_module.app

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
