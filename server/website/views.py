import json

from pydantic import ValidationError

from django.shortcuts import render, redirect
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from website.PydanticModels import RegUser, EnterUser, EditUser, CreatedServices
from website.support_code import auth
from website.support_code.MyResponse import MyResponse
from website.MVCmodels import (reg_user, enter_user, model_services_sector, model_services, model_edit_user,
                               model_create_service)
from website.support_code.MySerialize import serialize
from website.models import TypesService, Sessions, Services


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


@csrf_exempt
@auth.use_auth
def edit_personal_data(request: HttpRequest, user_id: int, session: Sessions):
    try:
        user = EditUser(**json.loads(request.body))
    except ValidationError as e:
        error: list = e.errors()
        response = MyResponse([], 400, error)
        return JsonResponse(response.to_dict(), status=response.response_status)
    user = model_edit_user(user_id, user)

    data = [{
        "type_obj": "users",
        "fields": serialize(user, ("password",))
    }]
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

    services = model_services(type_services, req_sectors, user_id)

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
def post_controller_services(request: HttpRequest, session: Sessions, user_id=None):
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


def main_controller_user_services(request: HttpRequest, services_id: int = None):
    if request.method == "GET":
        return get_controller_user_services(request, services_id)
    elif request.method == "PATCH":
        pass
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
def patch_controller_service()
