import enum

from django.db import models


# Create your models here.
class Users(models):
    name = models.TextField()
    phone = models.TextField(max_length=11)
    email = models.TextField()
    password = models.TextField()

    about_user = models.TextField(null=True)
    payer_number = models.TextField(max_length=12, null=True)
    state_number = models.TextField(max_length=15, null=True)
    role = models.TextField(null=True)


class UserRoles(enum.Enum):
    customer = "заказчик"
    engineer = "инжинер"
    company = "уполномоченный от предприятия"
