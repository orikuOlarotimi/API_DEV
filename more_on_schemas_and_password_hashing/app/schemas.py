from pydantic import BaseModel, EmailStr
from datetime import datetime


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(Post):
    pass


class PostBase(Post):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Usercreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True
