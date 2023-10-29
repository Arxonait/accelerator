import enum

from django.db import models


# Create your models here.
class Users(models.Model):
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


class ServiceSectors(models.Model):
    name_sector = models.TextField()
    about = models.TextField()


class Services(models.Model):
    user = models.ForeignKey("Users", on_delete=models.CASCADE)
    sector = models.ForeignKey("ServiceSectors", on_delete=models.CASCADE)

    type_service = models.TextField()

    name_service = models.TextField()
    price = models.FloatField()
    about = models.TextField()

    name_company = models.TextField(null=True)


class TypesService(enum.Enum):
    engineer = "инжинер"
    company = "предприятие"


