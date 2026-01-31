from typing import Literal
from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class MessageType(Enum):
    WELCOME = "session_welcome"
    KEEPALIVE = "session_keepalive"
    NOTIFICATION = "notification"
    RECONNECT = "session_reconnect"
    REVOKE = "revocation"


class Metadata(BaseModel):
    message_id: str
    message_type: MessageType
    message_timestamp: datetime


class NotificationMetadata(BaseModel):
    message_id: str
    message_type: Literal[MessageType.NOTIFICATION]
    message_timestamp: datetime
    subscription_type: (
        Literal["channel.chat.message"] | Literal["channel.suspicious_user.message"]
    )
    subscription_version: str


class Subscription(BaseModel):
    id: str
    status: str
    type: str
    version: str
    cost: int
    condition: dict
    transport: dict
    created_at: datetime


class ChannelChatMessage(BaseModel):
    broadcaster_user_id: str
    broadcaster_user_login: str
    broadcaster_user_name: str
    chatter_user_id: str
    chatter_user_login: str
    chatter_user_name: str
    message_id: str
    message: dict
    color: str
    badges: list
    message_type: str
    cheer: str | None = None
    reply: str | None = None
    channel_points_custom_reward_id: str | None = None
    source_broadcaster_user_id: str | None = None
    source_broadcaster_user_login: str | None = None
    source_broadcaster_user_name: str | None = None
    source_message_id: str | None = None
    source_badges: list[dict] | None = None
    is_source_only: bool


class Session(BaseModel):
    pass


class Payload(BaseModel):
    session: Session | None = None
    subscription: Subscription | None = None
    event: ChannelChatMessage | None = None


class Message(BaseModel):
    metadata: Metadata
    payload: Payload


class SessionPayload(BaseModel):
    pass


class WelcomeMessage(BaseModel):
    pass


class KeepaliveMessage(BaseModel):
    pass


class NotificationMessage(BaseModel):
    pass


class ReconnectMessage(BaseModel):
    pass


class RecovationMessage(BaseModel):
    pass
