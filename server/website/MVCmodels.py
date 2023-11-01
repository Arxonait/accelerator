import datetime
import json
import uuid
from typing import Tuple

from website.models import *
from website.PydanticModels import RegUser, EnterUser, EditUser
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


def model_services(type_services: str, sectors: list[str] | None = None):
    services = Services.objects.filter(type_service=type_services).select_related("sector", "user")
    if sectors is not None:
        services = services.filter(sector__slug__in=sectors)
    return services


def model_edit_user(user_id: int, user: EditUser):
    user_bd = User.objects.filter(id=user_id)[0]
    data = user.model_dump(exclude={"unstructured_data"}, exclude_none=True)
    # filtered_data = {key: value for key, value in data.items() if value is not None}
    if "birthday" in data:
        data["birthday"] = datetime.datetime.utcfromtimestamp(data["birthday"])
    User.objects.filter(id=user_id).update(**data)

    if user.unstructured_data is not None:
        uns_data = user.unstructured_data.model_dump(exclude_none=True)
        if user_bd.unstructured_data is None:
            uns_data_bd = {}
        else:
            uns_data_bd = json.loads(user_bd.unstructured_data)
        unstructured_data = uns_data_bd.update(uns_data)
        print(unstructured_data)
        #user_bd.unstructured_data = user_bd.unstructured_data.update(uns_data)
        user_bd.save()

    return user_bd
