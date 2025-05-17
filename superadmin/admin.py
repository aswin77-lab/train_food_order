from django.contrib import admin

from .models import Station, TrainRoute

admin.site.register(Station)
admin.site.register(TrainRoute)