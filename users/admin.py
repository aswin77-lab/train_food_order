from django.contrib import admin

from .models import CustomUser,Trip,Order

admin.site.register(Trip)
admin.site.register(CustomUser)
admin.site.register(Order)
