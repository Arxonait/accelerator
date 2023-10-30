from django.urls import path, include

from website import views

urlpatterns = [
    path("api/reg", views.registration_user_json),
    path("api/login", views.login_json),
    path("api/services", views.service_sector_json),

    path("/", views.load_page_main)
]