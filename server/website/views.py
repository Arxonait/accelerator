import json


from pydantic import ValidationError

from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from website.PydanticModels import RegUser, EnterUser
from website.support_code.MyResponse import MyResponse
from website.MVCmodels import reg_user, enter_user
from website.support_code.MySerialize import serialize


# Create your views here.
@csrf_exempt
def registration_user(request: HttpRequest):
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
def login(request: HttpRequest):
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
    return JsonResponse(response.to_dict(), status=response.response_status)