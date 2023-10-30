import uuid
from typing import Tuple

from website.models import *
from website.PydanticModels import RegUser, EnterUser
from website.support_code.hash_password import convert_password_to_hash
from django.db import IntegrityError


def reg_user(input_user: RegUser) -> User:
    name = f"{input_user.name} {input_user.surname}"
    user = User(name=name, password=convert_password_to_hash(input_user.password), email=input_user.email)
    try:
        user.save()
    except IntegrityError as e:
        raise Exception(e.args[0])
    return user


def enter_user(input_user: EnterUser) -> Tuple[User, Sessions]:
    user = User.objects.filter(email=input_user.email)
    if len(user) == 0:
        raise Exception(f"No found user with email: {input_user.email}")
    user = user[0]
    if user.password != convert_password_to_hash(input_user.password):
        raise Exception("Wrong password")
    session_id = uuid.uuid4()
    session = Sessions(session=str(session_id), user_id=user.pk)
    session.save()
    return user, session


def model_services_sector():
    services_sector = ServiceSectors.objects.filter()
    return services_sector
