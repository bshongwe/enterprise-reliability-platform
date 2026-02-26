import os
os.environ['API_KEY'] = 'test-key'

from common.audit import audit_log
from common.metrics import http_requests_total

def test_audit_log():
    result = audit_log("user1", "test_action", "entity1", "success")
    assert result is not None

def test_metrics_counter():
    metric = http_requests_total.labels(
        service="test",
        method="GET",
        endpoint="/test",
        status="success"
    )
    before = metric._value.get()
    metric.inc()
    after = metric._value.get()
    assert after == before + 1
