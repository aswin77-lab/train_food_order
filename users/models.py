# users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.conf import settings

from superadmin.models import TrainRoute
from vendors.models import FoodItem, Vendor


GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
)

class CustomUser(AbstractUser):
    # Additional fields for our custom user model
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return self.username


class Trip(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    train_route = models.ForeignKey(TrainRoute, on_delete=models.CASCADE)
    travel_date = models.DateField()
    booking_time = models.DateTimeField(auto_now_add=True)
    pnr = models.CharField(max_length=10, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pnr:
            self.pnr = str(uuid.uuid4()).split('-')[0].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Trip {self.pnr} by {self.user.username}"

class Order(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    order_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,null=True)  # Linking to Vendor


    def __str__(self):
        return f"Order {self.id} - {self.user}"