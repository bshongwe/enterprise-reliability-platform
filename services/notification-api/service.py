from services.notification_api.models import NotificationRequest
from common.audit import audit_log

notifications_db = {}


def send_notification(notification: NotificationRequest, user: str):
    notification_id = f"notif_{len(notifications_db)+1}"

    notifications_db[notification_id] = {
        **notification.dict(),
        "status": "PENDING"
    }

    try:
        # Simulate notification delivery
        if notification.channel == "slack":
            delivery_status = "DELIVERED"
        elif notification.channel == "email":
            delivery_status = "DELIVERED"
        else:
            delivery_status = "FAILED"

        notifications_db[notification_id]["status"] = delivery_status
        audit_log(
            user,
            "send_notification",
            notification_id,
            "success"
        )
        return notification_id, delivery_status
    except Exception as e:
        notifications_db[notification_id]["status"] = "FAILED"
        audit_log(
            user,
            "send_notification",
            notification_id,
            "fail",
            f"error={type(e).__name__}"
        )
        raise
