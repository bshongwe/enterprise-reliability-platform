from pydantic import BaseModel, validator


class NotificationRequest(BaseModel):
    recipient: str
    channel: str
    subject: str
    message: str

    @validator('channel')
    def channel_allowed(cls, v):
        allowed = {"slack", "email"}
        if v not in allowed:
            raise ValueError(f"Channel must be one of {allowed}")
        return v


class NotificationResponse(BaseModel):
    notification_id: str
    status: str
    message: str
