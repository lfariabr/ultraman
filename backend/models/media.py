from django.db import models
from athletes.models.athlete import Athlete
from athletes.models.race import Race
from athletes.models.photographer import Photographer
from athletes.models.coach import Coach
from athletes.models.staff import Staff
from athletes.models.brand import Brand
from athletes.models.club import Club
from athletes.models.media_type_choices import MediaTypeChoices
from athletes.models.activity_type_choices import ActivityTypeChoices

class Media(models.Model):
    athlete = models.ForeignKey(
        Athlete,
        related_name='media',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    other_athletes = models.ManyToManyField(
        Athlete,
        related_name='media_participants',
        blank=True
    )
    race = models.ForeignKey(
        Race,
        related_name='media',
        on_delete=models.CASCADE
    )
    photographer = models.ForeignKey(
        Photographer,
        related_name='media',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    coach = models.ManyToManyField(
        Coach,
        related_name='media',
        blank=True
    )
    staff = models.ManyToManyField(
        Staff,
        related_name='media',
        blank=True
    )
    brand = models.ManyToManyField(
        Brand,
        related_name='media',
        blank=True
    )
    club = models.ManyToManyField(
        Club,
        related_name='media',
        blank=True
    )

    file = models.FileField(upload_to='media/%Y/%m/%d/')
    file_type = models.CharField(max_length=30, choices=MediaTypeChoices.choices)
    activity_type = models.CharField(max_length=30, choices=ActivityTypeChoices.choices)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_type} - {self.athlete} - {self.activity_type}"