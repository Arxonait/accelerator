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
    def wrapper(request: HttpRequest, user_id: int = None, *args, **kwargs):
        session_id = request.COOKIES.get("session_id")
        response: MyResponse
        try:
            session = session_is_valid(session_id)
        except Exception as e:
            response = MyResponse([], 401, [str(e)])
            return JsonResponse(response.to_dict(), status=response.response_status)

        if user_id is not None:
            if session.user.pk != user_id:
                error = "No access"
                response = MyResponse([], 403, [error])
                return JsonResponse(response.to_dict(), status=response.response_status)

        session, status_update = time_to_update_session(session)
        response: JsonResponse = func(request=request, *args, session=session, **kwargs)
        if status_update:
            response.set_cookie("session_id", session.session, max_age=EXP_SESSION)
        return response

    return wrapper


def update_session(session: Sessions):
    session.time_created = datetime.datetime.utcnow()
    session.save()
    return session


def time_to_update_session(session: Sessions):
    time_created = session.time_created.astimezone(pytz.timezone("UTC"))
    now = datetime.datetime.now().astimezone(pytz.timezone("UTC"))
    if now - time_created > EXP_SESSION/2:
        session = update_session(session)
        return session, True
    return session, False
