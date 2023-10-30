import datetime

import pytz
from django.http import HttpRequest, JsonResponse

from website.models import Sessions
from website.support_code.MyResponse import MyResponse

EXP_SESSION = datetime.timedelta(days=1)


def session_is_valid(session_id: str) -> Sessions:
    if session_id is None:
        raise Exception("Input session is none")
    sessions = Sessions.objects.filter(session=session_id)
    if len(sessions) == 0:
        raise Exception("No found session in bd")
    session: Sessions = sessions[0]
    time_created = session.time_created.astimezone(pytz.timezone('UTC'))
    now = datetime.datetime.now().astimezone(pytz.timezone("UTC"))
    if (now - time_created) > EXP_SESSION:
        raise Exception("Session dead")
    return session


def use_auth(func):
    def wrapper(*args, request: HttpRequest, **kwargs):
        session_id = request.COOKIES.get("session_id")
        try:
            session = session_is_valid(session_id)
        except Exception as e:
            response = MyResponse([], 401, [str(e)])
            return JsonResponse(response.to_dict(), status=response.response_status)
        return func(*args, **kwargs, session=session)

    return wrapper
