from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from core.models.user import SessionStatus

class Tokens(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_info: str = "Bearer"

class TokenBase(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
        from_attributes=True,
    )
    token_uuid: str
    ip_address: str
    status: SessionStatus = SessionStatus.ACTIVE
    sub: str

class TokenInfo(TokenBase):
    id: int
    timestamp: datetime

class TokenCreate(TokenBase):
    pass

class SessionBase(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
        from_attributes=True,
    )
    uuid: str
    name: str
    sub: str
    status: Optional[SessionStatus] = Field(
            default= SessionStatus.ACTIVE, validate_default=True
        )

class SessionCreate(SessionBase):
    status: SessionStatus = SessionStatus.ACTIVE

class SessionRead(SessionBase):
    id: str
    can_abort: bool
    timestamp: float

    @field_validator("timestamp", mode='before')
    def convert_datetime_to_timestamp(cls, v):
        if isinstance(v, datetime):
            return v.timestamp()
        return v