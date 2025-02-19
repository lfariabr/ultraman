from django.db import models

class Photographer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=30)

    def __str__(self):
        return self.name