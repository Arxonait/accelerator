import json

from pydantic import ValidationError

from django.shortcuts import render, redirect
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from website.PydanticModels import RegUser, EnterUser, EditUser, CreatedServices, EditService, PostApp, CreatedMessage
from website.support_code import auth
from website.support_code.MyResponse import MyResponse
from website.MVCmodels import *
from website.support_code.MySerialize import serialize
from website.models import TypesService, Sessions, Services, StatusApp, Applications, Messages


# Create your views here.
@csrf_exempt
def registration_user_json(request: HttpRequest):
    try:
        user = RegUser(**json.loads(request.body))
    except ValidationError as e:
        error: list = e.errors()
        response = MyResponse([], 400, error)
        return JsonResponse(response.to_dict(), status=response.response_status)

    try:
        user = reg_user(user)
    except Exception as e:
        error = [str(e)]
        response = MyResponse([], 400, error)
        return JsonResponse(response.to_dict(), status=response.response_status)

    user_dict = serialize(user, ("password",))
    data = [
        {
            "type_obj": "users",
            "field": user_dict
        }
    ]
    response = MyResponse(data, 201)
    return JsonResponse(response.to_dict(), status=response.response_status)


@csrf_exempt
def login_json(request: HttpRequest):
    try:
        user = EnterUser(**json.loads(request.body))
    except ValidationError as e:
        error: list = e.errors()
        response = MyResponse([], 400, error)
        return JsonResponse(response.to_dict(), status=response.response_status)

    try:
        user, session = enter_user(user)
    except Exception as e:
        error = [str(e)]
        response = MyResponse([], 400, error)
        return JsonResponse(response.to_dict(), status=response.response_status)

    user_dict = serialize(user, ("password",))
    data = [
        {
            "type_obj": "users",
            "field": user_dict
        }
    ]
    response = MyResponse(data, 200)
    response = JsonResponse(response.to_dict(), status=response.response_status)
    response.set_cookie("session_id", session.session, max_age=auth.EXP_SESSION)
    return response


def logout(request: HttpRequest):
    response = JsonResponse({"status": "ok"}, status=200)
    response.delete_cookie("session_id")
    return response


@csrf_exempt
@auth.use_auth
def edit_personal_data(request: HttpRequest, session: Sessions):
    try:
        edit_data_user = EditUser(**json.loads(request.body))
    except ValidationError as e:
        error: list = e.errors()
        response = MyResponse([], 400, error)
        return JsonResponse(response.to_dict(), status=response.response_status)
    edit_data_user = model_edit_user(session.user_id, edit_data_user)

    data = [
        {
            "type_obj": "users",
            "fields": serialize(edit_data_user, ("password",))
        }
    ]
    response = MyResponse(data, 200)
    return JsonResponse(response.to_dict(), status=response.response_status)


@csrf_exempt
def service_sector_json(request: HttpRequest):
    data = []
    services_sector = model_services_sector()
    for service in services_sector:
        data_dict = {
            "type_obj": "services_sector",
            "field": serialize(service)
        }
        data.append(data_dict)
    response = MyResponse(data, 200)
    return JsonResponse(response.to_dict(), status=response.response_status)


@auth.use_auth
def get_user_by_session_id(request: HttpRequest, session):
    user = session.user
    data = [
        {
            "type_obj": "users",
            "field": serialize(user, ("password",))
        }
    ]
    response = MyResponse(data, 200)
    return JsonResponse(response.to_dict(), status=response.response_status)


@csrf_exempt
def main_controller_services(request: HttpRequest, user_id: int = None):
    if request.method == "GET":
        return get_controller_services(request, user_id)
    elif request.method == "POST":
        return post_controller_services(request)
    else:
        error = f"Allowed method GET and POST"
        response = MyResponse([], 405, [error])
        return JsonResponse(response.to_dict(), status=response.response_status)


def get_controller_services(request: HttpRequest, user_id: int = None):
    type_services = request.GET.get("type_service")
    if type_services is not None:
        try:
            type_services = getattr(TypesService, type_services).value
        except AttributeError as e:
            error = f"Допустимые значения для type_services {[type_services_name.name for type_services_name in TypesService]}"
            response = MyResponse([], 409, [error])
            return JsonResponse(response.to_dict(), status=response.response_status)

    req_sectors: str = request.GET.get("sectors")
    if req_sectors is not None:
        req_sectors: list = req_sectors.replace(" ", "").split(",")

    price_gte = request.GET.get("price_gte")
    price_lte = request.GET.get("price_lte")
    search = request.GET.get("search")

    services = model_services(type_services, req_sectors, user_id, lte=price_lte, gte=price_gte, search=search)

    data = []
    for service in services:
        data.append({
            "type_obj": "services",
            "field": serialize(service),
            "relationship": support_include_services(service, request.GET.get("include"))
        })
    response = MyResponse(data, 200)
    return JsonResponse(response.to_dict(), status=response.response_status)


@auth.use_auth
def post_controller_services(request: HttpRequest, session: Sessions):
    try:
        input_service = CreatedServices(**json.loads(request.body))
    except ValidationError as e:
        error: list = e.errors()
        response = MyResponse([], 400, error)
        return JsonResponse(response.to_dict(), status=response.response_status)
    except Exception as e:
        error = [str(e)]
        response = MyResponse([], 400, error)
        return JsonResponse(response.to_dict(), status=response.response_status)

    try:
        service = model_create_service(input_service, session.user_id)
    except Exception as e:
        error = [str(e)]
        response = MyResponse([], 400, error)
        return JsonResponse(response.to_dict(), status=response.response_status)

    data = [
        {
            "type_obj": "services",
            "field": serialize(service)
        }
    ]
    response = MyResponse(data, 201)
    return JsonResponse(response.to_dict(), status=response.response_status)


def support_include_services(service: Services, include: str):
    if include is None:
        return []
    include = include.replace(" ", "").split(",")  # повторяющиеся операция
    relationship = []
    if "user" in include:
        data_user = {
            "type_obj": "users",
            "filed": serialize(service.user, ("password",))
        }
        relationship.append(data_user)
    if "sector" in include:
        data_sector = {
            "type_obj": "services_sector",
            "filed": serialize(service.sector)
        }
        relationship.append(data_sector)
    return relationship


@csrf_exempt
def main_controller_user_services(request: HttpRequest, services_id: int = None):
    if request.method == "GET":
        return get_controller_user_services(request, services_id)
    elif request.method == "PATCH":
        return patch_controller_user_service(request, services_id=services_id)
    else:
        error = f"Allowed method GET and PATCH"
        response = MyResponse([], 405, [error])
        return JsonResponse(response.to_dict(), status=response.response_status)


def get_controller_user_services(request: HttpRequest, services_id: int = None):
    services = model_services(services_id=services_id)
    if len(services) == 0:
        error = f"No found"
        response = MyResponse([], 404, [error])
        return JsonResponse(response.to_dict(), status=response.response_status)
    service = services[0]
    data = [
        {
            "type_obj": "services",
            "field": serialize(service),
            "relationship": support_include_services(service, request.GET.get("include"))
        }
    ]
    response = MyResponse(data, 200)
    return JsonResponse(response.to_dict(), status=response.response_status)


@auth.use_auth
def patch_controller_user_service(request: HttpRequest, services_id: int = None, session: Sessions = None):
    try:
        edit_data_service = EditService(**json.loads(request.body))
    except ValidationError as e:
        error: list = e.errors()
        response = MyResponse([], 400, error)
        return JsonResponse(response.to_dict(), status=response.response_status)
    except Exception as e:
        error = [str(e)]
        response = MyResponse([], 400, error)
        return JsonResponse(response.to_dict(), status=response.response_status)

    try:
        service = model_edit_service(services_id, session.user_id, edit_data_service)
    except Exception as e:
        error = [str(e)]
        response = MyResponse([], 403, error)
        return JsonResponse(response.to_dict(), status=response.response_status)

    data = [
        {
            "type_obj": "services",
            "field": serialize(service)
        }
    ]
    response = MyResponse(data, 201)
    return JsonResponse(response.to_dict(), status=response.response_status)


@csrf_exempt
def main_controller_user_applications(request: HttpRequest, user_id: int = None):
    if request.method == "GET":
        return get_controller_user_application(request, user_id)
    else:
        error = f"Allowed method GET"
        response = MyResponse([], 405, [error])
        return JsonResponse(response.to_dict(), status=response.response_status)


def get_controller_user_application(request: HttpRequest, user_id: int):
    statuses: str = request.GET.get("statuses")
    if statuses is not None:
        statuses: list[str] = statuses.replace(" ", "").split(",")
        try:
            support_validate_status_app(statuses)
        except Exception as e:
            response = MyResponse([], 409, [str(e)])
            return JsonResponse(response.to_dict(), status=response.response_status)

    apps = model_app(customer_id=user_id, status=statuses)

    data = []
    for app in apps:
        data_app = {
            "type_obj": "applications",
            "field": serialize(app),
            "relationship": support_include_app(app, request.GET.get("include"))
        }
        data.append(data_app)

    response = MyResponse(data, 200)
    return JsonResponse(response.to_dict(), status=response.response_status)


@csrf_exempt
def main_controller_applications(request: HttpRequest, app_id: int = None):
    if request.method == "GET":
        return get_controller_application(request, app_id)
    elif request.method == "POST":
        return post_controller_applications(request)
    else:
        error = f"Allowed method GET and POST"
        response = MyResponse([], 405, [error])
        return JsonResponse(response.to_dict(), status=response.response_status)


@auth.use_auth
def post_controller_applications(request: HttpRequest, session=None):
    try:
        new_app = PostApp(**json.loads(request.body))
    except ValidationError as e:
        error: list = e.errors()
        response = MyResponse([], 400, error)
        return JsonResponse(response.to_dict(), status=response.response_status)
    try:
        app = model_create_message(new_app)
    except Exception as e:
        error = [str(e)]
        response = MyResponse([], 400, error)
        return JsonResponse(response.to_dict(), status=response.response_status)

    data = [
        {
            "type_obj": "applications",
            "field": serialize(app)
        }
    ]
    response = MyResponse(data, 200)
    return JsonResponse(response.to_dict(), status=response.response_status)


def get_controller_application(request: HttpRequest, app_id: int):
    apps = model_app(app_id=app_id)
    if len(apps) == 0:
        error = f"No found"
        response = MyResponse([], 404, [error])
        return JsonResponse(response.to_dict(), status=response.response_status)

    app = apps[0]
    status_code = 200

    status = request.GET.get("status")
    if status is not None:
        try:
            support_validate_status_app([status])
        except Exception as e:
            response = MyResponse([], 409, [str(e)])
            return JsonResponse(response.to_dict(), status=response.response_status)

        app.status = status
        app.save()
        status_code = 202

    data = [
        {
            "type_obj": "applications",
            "field": serialize(app),
            "relationship": support_include_app(app, request.GET.get("include"))
        }
    ]
    response = MyResponse(data, status_code)
    return JsonResponse(response.to_dict(), status=response.response_status)


def support_validate_status_app(statuses: list[str]):
    for status in statuses:
        try:
            status = getattr(StatusApp, status).value
        except AttributeError as e:
            error = f"Допустимые значения для status {[status_name.name for status_name in StatusApp]}"
            raise Exception(error)


def support_include_app(app: Applications, include: str):
    if include is None:
        return []
    include = include.replace(" ", "").split(",")  # повторяющиеся операция
    relationship = []
    if "customer" in include:
        data_user = {
            "type_obj": "users",
            "filed": serialize(app.customer, ("password",))
        }
        relationship.append(data_user)
    if "executor" in include:
        data_sector = {
            "type_obj": "services",
            "filed": serialize(app.executor)
        }
        relationship.append(data_sector)
    return relationship


@csrf_exempt
def main_controller_application_messages(request: HttpRequest, app_id: int):
    if request.method == "GET":
        return get_controller_messages(request, app_id)
    elif request.method == "POST":
        return post_controller_messages(request, app_id=app_id)
    else:
        error = f"Allowed method GET and POST"
        response = MyResponse([], 405, [error])
        return JsonResponse(response.to_dict(), status=response.response_status)


@auth.use_auth
def post_controller_messages(request: HttpRequest, app_id: int, session: Sessions = None):
    try:
        input_message = CreatedMessage(**json.loads(request.body))
    except ValidationError as e:
        error: list = e.errors()
        response = MyResponse([], 400, error)
        return JsonResponse(response.to_dict(), status=response.response_status)

    message = model_create_message(input_message, app_id, session.user_id)

    data = [
        {
            "type_obj": "messages",
            "field": serialize(message),
        }
    ]
    response = MyResponse(data, 201)
    return JsonResponse(response.to_dict(), status=response.response_status)


def get_controller_messages(request: HttpRequest, app_id: int):
    apps = model_app(app_id=app_id)
    if len(apps) == 0:
        error = f"No found"
        response = MyResponse([], 404, [error])
        return JsonResponse(response.to_dict(), status=response.response_status)

    app = apps[0]
    mess = model_mess(app_id)
    data = []
    for mes in mess:
        data_mess = {
            "type_obj": "messages",
            "field": serialize(mes),
        }
        data.append(data_mess)

    include: str = request.GET.get("include")
    if include is not None:
        include: list[str] = include.replace(" ", "").split(",")
        if "application" in include:
            data_app = {
                "type_obj": "applications",
                "field": serialize(app)
            }
            data.append(data_app)

    response = MyResponse(data, 200)
    return JsonResponse(response.to_dict(), status=response.response_status)