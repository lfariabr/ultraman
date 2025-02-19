from django.db import models
from athletes.models.athlete import Athlete

class Staff(models.Model):
    athlete = models.ForeignKey(Athlete, related_name='staff_members', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=30)
    role = models.CharField(max_length=50, blank=True, null=True)  # Optional role description

    def __str__(self):
        return self.name