import uuid

from server.website.models import *
from server.website.PydanticModels import RegUser, EnterUser
from server.website.support_code.hash_password import convert_password_to_hash
from django.db import IntegrityError


def reg_user(input_user: RegUser) -> User:
    name = f"{input_user.name} {input_user.surname}"
    user = User(name=name, password=convert_password_to_hash(input_user.password), email=input_user.email)
    try:
        user.save()
    except IntegrityError as e:
        if 'unique constraint' in e.args[0]:
            text_exc = "unique constraint"
        else:
            text_exc = "another error with create user"
        raise Exception(text_exc)
    return user


def enter_user(input_user: EnterUser) -> (User, Sessions):
    user = User.objects.filter(email=input_user.email)
    if len(user) == 0:
        raise Exception(f"No found user with email: {input_user.email}")
    if user.password != convert_password_to_hash(input_user.password):
        raise Exception("Wrong password")
    user = user[0]
    session_id = uuid.uuid4()
    session = Sessions(session=session_id)
    session.save()
    return user, session
