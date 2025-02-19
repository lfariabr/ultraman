from django.db import models
from django.core.exceptions import ValidationError
from athletes.models.athlete import Athlete
from athletes.models.race import Race

class Results(models.Model):
    athlete = models.ForeignKey(Athlete, related_name='results', on_delete=models.CASCADE)
    race = models.ForeignKey(Race, related_name='results', on_delete=models.CASCADE)
    race_swim_10km_time = models.DurationField()
    race_swim_10km_rank = models.IntegerField()
    race_bike_145km_time = models.DurationField()
    race_bike_145km_rank = models.IntegerField()
    race_bike_276km_time = models.DurationField()
    race_bike_276km_rank = models.IntegerField()
    race_run_84km_time = models.DurationField()
    race_run_84km_rank = models.IntegerField()
    race_overall_time = models.DurationField()
    race_overall_rank = models.IntegerField()

    class Meta:
        unique_together = ['athlete', 'race']

    def __str__(self):
        return f"{self.athlete.complete_name} - {self.race.race_edition} - Rank: {self.race_overall_rank}"
    
    def clean(self):
        # Validate non-null times first
        for field_name in ['race_swim_10km_time', 'race_bike_145km_time', 'race_bike_276km_time', 'race_run_84km_time', 'race_overall_time']:
            value = getattr(self, field_name)
            if value is None:
                raise ValidationError({field_name: 'Time cannot be null'})

        # Validate total duration matches segment times
        total_duration = (
            self.race_swim_10km_time +
            self.race_bike_145km_time +
            self.race_bike_276km_time +
            self.race_run_84km_time
        )
        if self.race_overall_time != total_duration:
            raise ValidationError('Overall time is not equal to the sum of the individual times')

        # Validate positive ranks
        for field_name in ['race_swim_10km_rank', 'race_bike_145km_rank', 'race_bike_276km_rank', 'race_run_84km_rank', 'race_overall_rank']:
            value = getattr(self, field_name)
            if value <= 0:
                raise ValidationError({field_name: 'Rank must be a positive number'})