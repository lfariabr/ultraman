from django.db import models
from athletes.models.club import Club

class Coach(models.Model):
    name = models.CharField(max_length=100)
    club = models.ForeignKey(Club, related_name='coaches', on_delete=models.CASCADE)
    email = models.EmailField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    # Add more fields as necessary

    def __str__(self):
        return self.name