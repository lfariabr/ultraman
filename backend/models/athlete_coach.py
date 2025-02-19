from django.db import models

from athletes.models.athlete import Athlete
from athletes.models.coach import Coach

class AthleteCoach(models.Model):
    athlete = models.ForeignKey(Athlete, related_name='athlete_coaches', on_delete=models.CASCADE)
    coach = models.ForeignKey(Coach, related_name='athlete_associations', on_delete=models.CASCADE)
    # Add fields like start_date, end_date if coaches can be associated over time

    def __str__(self):
        return f"{self.athlete.complete_name} - {self.coach.name}"