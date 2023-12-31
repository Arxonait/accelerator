import datetime
import json
import uuid
from typing import Tuple

from pytz import timezone

from website.models import *
from website.PydanticModels import *
from website.support_code.hash_password import convert_password_to_hash
from django.db import IntegrityError


def reg_user(input_user: RegUser) -> User:
    user = User(name=input_user.name, surname=input_user.surname,
                password=convert_password_to_hash(input_user.password),
                email=input_user.email)
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


def model_services(type_services: str = None, sectors: list[str] = None, user_id: int = None,
                   services_id: int = None, gte: int = None, lte: int = None, search: str = None) -> list[Services]:
    condition = dict()
    if type_services is not None:
        condition["type_service"] = type_services
    if sectors is not None:
        condition["sector__slug__in"] = sectors
    if user_id is not None:
        condition["user_id"] = user_id
    if services_id is not None:
        condition["pk"] = services_id
    if search is not None:
        condition["name_service__icontains"] = search
    if gte is not None:
        condition["price__gte"] = gte
    if lte is not None:
        condition["price__lte"] = lte
    services = Services.objects.filter(**condition).select_related("sector", "user").order_by("-time_created")
    return services


def model_create_service(new_service: CreatedServices, user_id: int):
    # todo перейти на англ !!!
    service = Services(user_id=user_id, sector_id=new_service.sector, type_service=new_service.type_service.value,
                       name_service=new_service.name_service, price=new_service.price, about=new_service.about)
    if new_service.type_service == TypesService.company:
        service.name_company = new_service.name_company
    try:
        service.save()
    except IntegrityError as e:
        raise Exception(e.args[0])
    return service


def model_edit_service(service_id: int, user_id: int, service: EditService):
    service_bd: Services = Services.objects.filter(id=service_id)[0]
    if service_bd.user_id != user_id:
        raise Exception("Not allowed edit service")
    data = service.model_dump(exclude_none=True)
    Services.objects.filter(id=service_id).update(**data)
    service_bd.refresh_from_db()
    return service_bd


def model_edit_user(user_id: int, user: EditUser):
    data = user.model_dump(exclude={"unstructured_data"}, exclude_none=True)
    data["role"] = user.role.value
    User.objects.filter(id=user_id).update(**data)  # запрос к бд
    # todo возмжно ли update email !!!

    user_bd: User = User.objects.filter(id=user_id)[0]  # запрос к бд
    if user.unstructured_data is not None:
        uns_data = user.unstructured_data.model_dump(exclude_none=True)
        if user_bd.unstructured_data is None:
            uns_data_bd = dict()
        else:
            uns_data_bd = json.loads(user_bd.unstructured_data)
        uns_data_bd.update(uns_data)
        user_bd.unstructured_data = json.dumps(uns_data_bd)
    user_bd.save()  # запрос к бд
    return user_bd


def model_create_app(new_app: PostApp):
    app = Applications(customer_id=new_app.customer_id, executor_id=new_app.executor_id)
    # создание у самого себя
    try:
        app.save()
    except IntegrityError as e:
        raise Exception(e.args[0])
    return app


def model_app(app_id: int = None, customer_id: int = None, status: list[str] = None) -> list[Applications]:
    condition = dict()
    if app_id is not None:
        condition["pk"] = app_id
    if customer_id is not None:
        condition["customer_id"] = customer_id
    if status is not None:
        condition["status__in"] = status
    apps = Applications.objects.filter(**condition).select_related("customer", "executor").order_by("-time_created")
    return apps


def model_create_message(new_mess: CreatedMessage, app_id: int, user_id: int):
    # todo настроить дуступ для пользователей
    mess = Messages(application_id=app_id, main_text=new_mess.main_text, user_id=user_id)
    # создание у самого себя
    try:
        mess.save()
    except IntegrityError as e:
        raise Exception(e.args[0])
    return mess


def model_mess(app_id: int) -> list[Messages]:
    condition = dict()
    mess = Messages.objects.filter(application_id=app_id).order_by("-time_created")
    return mess