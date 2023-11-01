from typing import Optional

from pydantic import BaseModel, Field


class RegUser(BaseModel):
    name: str
    surname: str
    email: str = Field(pattern=r"[a-zA-z0-9]+@[a-zA-z0-9]+\.[a-zA-z]+")
    password: str


class EnterUser(BaseModel):
    email: str = Field(pattern=r"[a-zA-z0-9]+@[a-zA-z0-9]+\.[a-zA-z]+")
    password: str


class UnstructuredDataUser(BaseModel):
    about_user: Optional[str] = None
    education: Optional[str] = None
    qualification: Optional[str] = None
    payer_number: Optional[str] = None

    name_company: Optional[str] = None
    products: Optional[str] = None
    tech_spec_prod: Optional[str] = None
    equipment_tech: Optional[str] = None
    services: Optional[str] = None
    terms_cooperation: Optional[str] = None


class EditUser(BaseModel):
    name: Optional[str] = None
    second_name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    birthday: Optional[int] = None

    unstructured_data: Optional[UnstructuredDataUser] = None

