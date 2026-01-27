from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )
    username: str

class UserRead(UserBase):
    id: str

class UserAuth(UserRead):
    pass

class UserReg(UserBase):
    pass
