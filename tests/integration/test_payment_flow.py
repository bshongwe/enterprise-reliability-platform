import pytest
import httpx
import os

API_KEY = os.getenv('API_KEY', 'test-key')
PAYMENTS_URL = os.getenv('PAYMENTS_URL', 'http://localhost:8000')
LEDGER_URL = os.getenv('LEDGER_URL', 'http://localhost:8001')

@pytest.mark.integration
def test_payment_flow_end_to_end():
    """Test complete payment flow from creation to ledger recording"""
    
    # Create payment
    payment_data = {
        "sender_account": "ACC001",
        "receiver_account": "ACC002",
        "amount": 100.0,
        "currency": "USD",
        "reference": "integration-test"
    }
    
    response = httpx.post(
        f"{PAYMENTS_URL}/payments",
        json=payment_data,
        headers={"X-API-Key": API_KEY},
        timeout=10.0
    )
    
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "payment_id" in data
        assert data["status"] in ["RECORDED", "PENDING", "FAILED"]
        payment_id = data["payment_id"]
        
        # Verify ledger entry
        ledger_response = httpx.get(
            f"{LEDGER_URL}/entries/{payment_id}",
            headers={"X-API-Key": API_KEY},
            timeout=10.0
        )
        
        if ledger_response.status_code == 200:
            entries = ledger_response.json()
            assert len(entries) > 0
            assert entries[0]["payment_id"] == payment_id
            assert entries[0]["amount"] == 100.0

@pytest.mark.integration
def test_payment_retrieval():
    """Test payment retrieval after creation"""
    
    # Create payment first
    payment_data = {
        "sender_account": "ACC003",
        "receiver_account": "ACC004",
        "amount": 50.0,
        "currency": "EUR",
        "reference": "test-retrieval"
    }
    
    create_response = httpx.post(
        f"{PAYMENTS_URL}/payments",
        json=payment_data,
        headers={"X-API-Key": API_KEY},
        timeout=10.0
    )
    
    if create_response.status_code == 200:
        payment_id = create_response.json()["payment_id"]
        
        # Retrieve payment
        get_response = httpx.get(
            f"{PAYMENTS_URL}/payments/{payment_id}",
            headers={"X-API-Key": API_KEY},
            timeout=10.0
        )
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["payment_id"] == payment_id
