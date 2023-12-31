import enum

from django.db import models


# Create your models here.
class User(models.Model):
    name = models.TextField()
    surname = models.TextField()
    second_name = models.TextField(null=True)
    phone = models.TextField(max_length=11, null=True)
    email = models.TextField(unique=True)
    birthday = models.DateTimeField(null=True)
    password = models.TextField()

    unstructured_data = models.TextField(null=True)
    role = models.TextField(null=True)


class UserRoles(enum.Enum):
    customer = "customer"
    engineer = "engineer"
    company = "company"


class Sessions(models.Model):
    session = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE)


class ServiceSectors(models.Model):
    name_sector = models.TextField()
    about = models.TextField()
    image_url = models.TextField()
    slug = models.TextField()


class Services(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    sector = models.ForeignKey("ServiceSectors", on_delete=models.CASCADE)

    type_service = models.TextField()

    name_service = models.TextField()
    price = models.FloatField()
    about = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)

    name_company = models.TextField(null=True)


class TypesService(enum.Enum):
    engineer = "engineer"
    company = "company"


class StatusApp(enum.Enum):
    processing = "processing"
    denied = "denied"
    completed = "completed"
    nviewed = "nviewed"


class Applications(models.Model):
    executor = models.ForeignKey("Services", on_delete=models.CASCADE)
    customer = models.ForeignKey("User", on_delete=models.CASCADE)
    status = models.TextField(default=StatusApp.nviewed.value)
    time_created = models.DateTimeField(auto_now_add=True)


class Messages(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    application = models.ForeignKey("Applications", on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)
    main_text = models.TextField()
