import datetime
import json

from pydantic import ValidationError

from django.shortcuts import render, redirect
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from website.PydanticModels import RegUser, EnterUser
from website.support_code import auth
from website.support_code.MyResponse import MyResponse
from website.MVCmodels import reg_user, enter_user, model_services_sector
from website.support_code.MySerialize import serialize


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
        },
        {
            "type_obj": "sessions",
            "field": serialize(session)
        }
    ]
    response = MyResponse(data, 200)
    response = JsonResponse(response.to_dict(), status=response.response_status)
    response.set_cookie("session_id", session.session, max_age=datetime.timedelta(days=1))
    return response


def load_page_login(request: HttpRequest):
    return render(request, ...)


def load_page_reg(request: HttpRequest):
    return render(request, ...)


def load_page_main(request: HttpRequest):
    return render(request, ...)


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


def load_page_personal_cabinet(request: HttpRequest):
    session_id = request.COOKIES.get("session_id", None)
    try:
        session = auth.session_is_valid(session_id)
    except Exception as e:
        return redirect("/login")
    user = session.user
    return render(request, ...)


def get_user_on_session_id(request: HttpRequest):
    session_id = request.COOKIES.get("session_id", None)
    try:
        session = auth.session_is_valid(session_id)
    except Exception as e:
        response = MyResponse([], 404, [str(e)])
        return JsonResponse(response.to_dict(), status=response.response_status)
    user = session.user
    data = [
        {
            "type_obj": "users",
            "field": serialize(user)
        }
    ]
    response = MyResponse(data, 200)
    return JsonResponse(response.to_dict(), status=response.response_status)
