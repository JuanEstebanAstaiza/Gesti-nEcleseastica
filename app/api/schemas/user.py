from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    role: str = "member"


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: str | None = None
    password: str | None = None
    is_active: bool | None = None

