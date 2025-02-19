from django.db import models

class ActivityTypeChoices(models.TextChoices):
    SWIM = 'swim', 'Swim'
    BIKE = 'bike', 'Bike'
    RUN = 'run', 'Run'
    CEREMONY = 'ceremony', 'Ceremony'
    CHECKIN = 'checkin', 'Check-in'
    MUGSHOT = 'mugshot', 'Mugshot'
    FINISH_1ST_DAY = 'finish_1st_day', 'Finish 1st Day'
    FINISH_2ND_DAY = 'finish_2nd_day', 'Finish 2nd Day'
    FINISH_3RD_DAY = 'finish_3rd_day', 'Finish 3rd Day'