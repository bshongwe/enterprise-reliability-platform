# Notification API

Handles Slack and email notification delivery.

## SLO
- **Delivery Success Rate:** 99.5%
- **Purpose:** Slack/email notification delivery

## Endpoints

### POST /notifications
Send a notification via Slack or email.

**Request:**
```json
{
  "recipient": "user@example.com",
  "channel": "email",
  "subject": "Payment Processed",
  "message": "Your payment has been processed successfully."
}
```

**Response:**
```json
{
  "notification_id": "notif_1",
  "status": "DELIVERED",
  "message": "Notification sent"
}
```

## Run Locally

```bash
export API_KEY="your-key"
uvicorn services.notification_api.main:app --port 8002
```
