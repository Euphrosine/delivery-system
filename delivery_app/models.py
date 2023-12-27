from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    # Add related_name to avoid clashes
    groups = models.ManyToManyField('auth.Group', related_name='delivery_user_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='delivery_user_set', blank=True)


class DeliveryRequest(models.Model):
    customer_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    delivery_address = models.TextField()
    items = models.TextField()
    pickup_location = models.CharField(max_length=255)
    pickup_contact = models.CharField(max_length=15)
    delivery_date = models.DateField()


class DeliverySentForm(models.Model):
    transporter_name = models.CharField(max_length=255)
    transporter_contact = models.CharField(max_length=15)
    product_description = models.TextField()
    customer_name = models.CharField(max_length=255)
    customer_contact = models.CharField(max_length=15)
    customer_email = models.EmailField()
    delivery_address = models.TextField()
    delivery_date = models.DateField()

