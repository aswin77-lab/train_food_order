
from django.db import models

from superadmin.models import Station

class Vendor(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed passwords
    near_station = models.ForeignKey(Station, on_delete=models.SET_NULL, null=True, blank=True)
    is_approved = models.BooleanField(default=False)  # Admin approval field

    def __str__(self):
        return self.name


class FoodItem(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)  # Assuming vendor is the logged-in user
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='food_images/')
    price = models.DecimalField(max_digits=6, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.name