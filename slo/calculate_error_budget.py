#!/usr/bin/env python3
import os
import sys
import requests
from datetime import datetime, timedelta

PROMETHEUS_URL = os.getenv(
    "PROMETHEUS_URL", "http://localhost:9090"
)

SLO_TARGETS = {
    "payments": 0.9995,
    "ledger": 0.9999,
    "account-service": 0.999,
}

def query_prometheus(query):
    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": query}
    )
    result = response.json()
    if result["status"] == "success" and result["data"]["result"]:
        value = result["data"]["result"][0]["value"][1]
        # Validate against NaN injection
        if value in ("nan", "NaN", "NAN", "inf", "-inf"):
            return None
        try:
            float_value = float(value)
            # Check if the result is actually NaN or infinite
            if (float_value != float_value or
                    float_value == float('inf') or
                    float_value == float('-inf')):
                return None
            return float_value
        except (ValueError, TypeError):
            return None
    return None

def calculate_error_budget(service, slo_target):
    query = f"""
    sum(rate(http_requests_total{{
        service="{service}",status="success"}}[30d]))
    /
    sum(rate(http_requests_total{{service="{service}"}}[30d]))
    """
    
    success_rate = query_prometheus(query)
    if success_rate is None:
        print(f"No data for {service}")
        return None
    
    error_budget_allowed = 1 - slo_target
    error_rate_actual = 1 - success_rate
    error_budget_consumed = error_rate_actual / error_budget_allowed
    error_budget_remaining = 1 - error_budget_consumed
    
    return {
        "service": service,
        "slo_target": slo_target * 100,
        "success_rate": success_rate * 100,
        "error_budget_remaining": error_budget_remaining * 100,
        "status": "OK" if error_budget_remaining > 0 else "EXHAUSTED"
    }

def main():
    print("SLO Error Budget Report")
    print("=" * 60)
    print(f"Generated: {datetime.now().isoformat()}")
    print()
    
    for service, slo_target in SLO_TARGETS.items():
        result = calculate_error_budget(service, slo_target)
        if result:
            print(f"Service: {result['service']}")
            print(f"  SLO Target: {result['slo_target']:.2f}%")
            print(f"  Success Rate: {result['success_rate']:.4f}%")
            print(
                f"  Error Budget Remaining: "
                f"{result['error_budget_remaining']:.2f}%"
            )
            print(f"  Status: {result['status']}")
            print()
            
            if result['error_budget_remaining'] < 10:
                print("  ⚠️  WARNING: Low error budget!")
                sys.exit(1)

if __name__ == "__main__":
    main()
