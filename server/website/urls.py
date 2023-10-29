from django.urls import path, include

from website import views

urlpatterns = [
    path("api/reg", views.registration_user),
    path("api/login", views.login),
]