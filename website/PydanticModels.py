from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator, ValidationError, field_validator, model_validator, model_serializer
from pytz import timezone
from website.models import TypesService, StatusApp, UserRoles


class RegUser(BaseModel):
    name: str
    surname: str
    email: str = Field(pattern=r"[a-zA-z0-9]+@[a-zA-z0-9]+\.[a-zA-z]+")
    password: str


class EnterUser(BaseModel):
    email: str = Field(pattern=r"[a-zA-z0-9]+@[a-zA-z0-9]+\.[a-zA-z]+")
    password: str


class UnstructuredDataUser(BaseModel):
    about_user: str = None
    education: str = None
    qualification: str = None
    payer_number: str = None

    name_company: str = None
    products: str = None
    tech_spec_prod: str = None
    equipment_tech: str = None
    services: str = None
    terms_cooperation: str = None


class EditUser(BaseModel):
    name: str = None
    second_name: str = None
    surname: str = None
    email: str = None
    phone: str = None
    birthday: int = None  # unix время в часовом поясе UTC
    role: UserRoles = None

    unstructured_data: Optional[UnstructuredDataUser] = None

    @validator('birthday')
    def convert_unix_to_datetime(cls, v):
        if v is not None:
            date = datetime.utcfromtimestamp(v)
            return date.replace(tzinfo=timezone("Europe/London"))
        return None


class CreatedServices(BaseModel):
    sector: int

    type_service: TypesService

    name_service: str
    price: int
    about: str
    name_company: str = None

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'CreatedServices':
        if self.type_service == TypesService.engineer and self.name_company is not None:
            raise Exception('Для инженера не должно быть имя предприятия')
        elif self.type_service == TypesService.company and self.name_company is None:
            raise Exception('Для предприятия должно быть имя предприятия')
        else:
            return self

    @model_serializer()
    def serialize(self):
        ser = self.__dict__.copy()
        if ser["type_service"] is not None:
            ser["type_service"] = ser["type_service"].value
        ser_exc_none = dict()
        for key in ser:
            if ser[key] is not None:
                ser_exc_none[key] = ser[key]
        return ser_exc_none


class EditService(CreatedServices):
    sector: int = Field(default=None, serialization_alias="sector_id")

    type_service: TypesService = Field(default=None)

    name_service: str = Field(default=None)
    price: int = Field(default=None)
    about: str = Field(default=None)
    name_company: str = Field(default=None)


class PostApp(BaseModel):
    executor_id: int
    customer_id: int


class CreatedMessage(BaseModel):
    main_text: str
