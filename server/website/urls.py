from django.urls import path, include

from website import views

urlpatterns = [
    path("api/reg", views.registration_user_json),
    path("api/login", views.login_json),
    path("api/services_sector", views.service_sector_json),
    path("api/session_to_user", views.get_user_on_session_id),

    path("/", views.load_page_main),
    path("/login", views.load_page_login),

]