from django.db import models

class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    contact_name = models.CharField(max_length=100, blank=True, null=True)
    contact_phone = models.CharField(max_length=30, blank=True, null=True)
    contact_email = models.EmailField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name