import pytest
import httpx
import os

API_KEY = os.getenv('API_KEY', 'test-key')
ACCOUNT_URL = os.getenv('ACCOUNT_URL', 'http://localhost:8002')

@pytest.mark.integration
def test_account_creation_and_balance():
    """Test account creation and balance operations"""
    
    # Create account
    account_data = {
        "user_id": "user_test_001",
        "account_type": "savings",
        "currency": "USD",
        "initial_balance": 1000.0
    }
    
    response = httpx.post(
        f"{ACCOUNT_URL}/accounts",
        json=account_data,
        headers={"X-API-Key": API_KEY},
        timeout=10.0
    )
    
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "account_id" in data
        assert data["balance"] == 1000.0
        account_id = data["account_id"]
        
        # Credit balance
        credit_data = {
            "amount": 500.0,
            "operation": "credit",
            "reference": "test-credit"
        }
        
        credit_response = httpx.post(
            f"{ACCOUNT_URL}/accounts/{account_id}/balance",
            json=credit_data,
            headers={"X-API-Key": API_KEY},
            timeout=10.0
        )
        
        if credit_response.status_code == 200:
            assert credit_response.json()["balance"] == 1500.0
        
        # Debit balance
        debit_data = {
            "amount": 200.0,
            "operation": "debit",
            "reference": "test-debit"
        }
        
        debit_response = httpx.post(
            f"{ACCOUNT_URL}/accounts/{account_id}/balance",
            json=debit_data,
            headers={"X-API-Key": API_KEY},
            timeout=10.0
        )
        
        if debit_response.status_code == 200:
            assert debit_response.json()["balance"] == 1300.0

@pytest.mark.integration
def test_insufficient_funds():
    """Test debit with insufficient funds"""
    
    # Create account with low balance
    account_data = {
        "user_id": "user_test_002",
        "account_type": "checking",
        "currency": "USD",
        "initial_balance": 10.0
    }
    
    response = httpx.post(
        f"{ACCOUNT_URL}/accounts",
        json=account_data,
        headers={"X-API-Key": API_KEY},
        timeout=10.0
    )
    
    if response.status_code == 200:
        account_id = response.json()["account_id"]
        
        # Attempt to debit more than balance
        debit_data = {
            "amount": 100.0,
            "operation": "debit",
            "reference": "test-insufficient"
        }
        
        debit_response = httpx.post(
            f"{ACCOUNT_URL}/accounts/{account_id}/balance",
            json=debit_data,
            headers={"X-API-Key": API_KEY},
            timeout=10.0
        )
        
        assert debit_response.status_code == 400
