import os
os.environ['API_KEY'] = 'test-key'

from common.audit import audit_log
from common.metrics import http_requests_total

def test_audit_log():
    audit_log("user1", "test_action", "entity1", "success")
    assert True

def test_metrics_counter():
    http_requests_total.labels(
        service="test",
        method="GET",
        endpoint="/test",
        status="success"
    ).inc()
    assert True
