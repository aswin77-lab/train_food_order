from django.db import models

class Station(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class TrainRoute(models.Model):
    train_number = models.CharField(max_length=50, unique=True)
    train_name = models.CharField(max_length=100)
    source_station = models.ForeignKey(Station, related_name="routes_from", on_delete=models.CASCADE)
    destination_station = models.ForeignKey(Station, related_name="routes_to", on_delete=models.CASCADE)
    intermediate_stops = models.ManyToManyField(Station, blank=True, related_name="intermediate_routes")
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    days_of_operation = models.CharField(
        max_length=100, 
        help_text="Comma-separated days (e.g., Mon,Tue,Wed)"
    )

    def __str__(self):
        return f"{self.train_number} - {self.train_name}"
