from django.db import models
from athletes.models.athlete import Athlete

class AthleteCurriculum(models.Model):
    athlete = models.ForeignKey(Athlete, related_name='curricula', on_delete=models.CASCADE)
    curriculum = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.athlete.complete_name} - Curriculum"