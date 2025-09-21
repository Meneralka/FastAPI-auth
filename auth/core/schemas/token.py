from datetime import datetime

from pydantic import BaseModel, ConfigDict
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
    status: SessionStatus = SessionStatus.ACTIVE

class SessionCreate(SessionBase):
    pass

class SessionRead(SessionBase):
    id: str
    can_abort: bool
    timestamp: datetime
