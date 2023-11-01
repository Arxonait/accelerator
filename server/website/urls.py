from django.urls import path, include

from website import views

urlpatterns = [
    path("api/reg", views.registration_user_json),
    path("api/login", views.login_json),
    path("api/services_sector", views.service_sector_json),
    path("api/session_to_user", views.get_user_by_session_id),
    path("api/services", views.main_controller_services),
    path("api/users/<int:user_id>", views.edit_personal_data),
    path("api/users/<int:user_id>/services", views.main_controller_services),
    path("api/services/<int:services_id>", views.main_controller_user_services),
]