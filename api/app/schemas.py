from pydantic import BaseModel, Field, EmailStr, HttpUrl
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(description="Name")
    created_at: datetime = Field(description="Created at")


class UserCreate(UserBase):
    pass


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True


class LoginCredentials(BaseModel):
    user: UserOut
    access_token: str


class DataToProcess(BaseModel):
    text: str | None = Field(min_length=3, description="Text to process")
    image_url: HttpUrl | None = Field(description="URL to image to process")


class TextResponse(BaseModel):
    provider: str
    response: str | None


class ImageResponse(BaseModel):
    type: str
    chance: float
