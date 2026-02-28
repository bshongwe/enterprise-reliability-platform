from pydantic import BaseModel, validator, Field
import re


class NotificationRequest(BaseModel):
    recipient: str = Field(..., max_length=255, min_length=1)
    channel: str
    subject: str = Field(..., max_length=200, min_length=1)
    message: str = Field(..., max_length=5000, min_length=1)

    @validator('channel')
    def channel_allowed(cls, v):
        allowed = {"slack", "email"}
        if v not in allowed:
            raise ValueError(f"Channel must be one of {allowed}")
        return v

    @validator('recipient')
    def validate_recipient(cls, v, values):
        channel = values.get('channel')
        if channel == 'email':
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v):
                raise ValueError('Invalid email address')
        elif channel == 'slack':
            if not v.startswith('@') and not v.startswith('#'):
                raise ValueError('Slack recipient must start with @ or #')
        return v

    @validator('subject', 'message')
    def sanitize_content(cls, v):
        # Remove potential injection characters
        dangerous_chars = ['\r', '\n', '\x00']
        for char in dangerous_chars:
            v = v.replace(char, '')
        return v.strip()


class NotificationResponse(BaseModel):
    notification_id: str
    status: str
    message: str
