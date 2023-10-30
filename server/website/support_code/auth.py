import datetime

from website.models import Sessions


def session_is_valid(session_id: str) -> Sessions:
    if session_id is None:
        raise Exception("Input session is none")
    sessions = Sessions.objects.filter(session=session_id)
    if len(sessions) == 0:
        raise Exception("No found session in bd")
    session = sessions[0]
    if datetime.datetime.utcnow() - session.time_created > datetime.timedelta(days=1):
        raise Exception("No session dead")
    return session
