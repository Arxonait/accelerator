from pydantic import BaseModel, Field


class RegUser(BaseModel):
    name: str
    surname: str
    email: str = Field(pattern=r"[a-zA-z0-9]+@[a-zA-z0-9]+\.[a-zA-z]+")
    password: str


class EnterUser(BaseModel):
    email: str = Field(pattern=r"[a-zA-z0-9]+@[a-zA-z0-9]+\.[a-zA-z]+")
    password: str
