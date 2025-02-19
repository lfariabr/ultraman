from django.db import models

class Race(models.Model):
    race_edition = models.CharField(max_length=30)
    race_date = models.DateField()
    race_location = models.CharField(max_length=100)  # Increased max_length for location names

    def __str__(self):
        return f"{self.race_edition} - {self.race_date} - {self.race_location}"