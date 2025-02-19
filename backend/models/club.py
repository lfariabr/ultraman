from django.db import models

class Club(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Increased max_length and added uniqueness
    description = models.TextField(blank=True, null=True)
    established_at = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name