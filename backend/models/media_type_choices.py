from django.db import models

class MediaTypeChoices(models.TextChoices):
    PHOTO = 'photo', 'Photo'
    VIDEO = 'video', 'Video'