from django.db import models
from athletes.models.gender_choice import GenderChoices

class Athlete(models.Model):
    # Basic
    complete_name = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=30)
    nickname = models.CharField(max_length=30, blank=True, null=True)  # Allowing nicknames to be optional

    # Personal
    created_at = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=30)
    email = models.EmailField(max_length=100, unique=True)  # Increased max_length and added unique constraint
    gender = models.CharField(
        max_length=10,
        choices=GenderChoices.choices,
        default=GenderChoices.OTHER
    )

    # Public for API
    eternal_number = models.CharField(max_length=30, unique=True)
    allowed_pictures = models.IntegerField()
    city = models.CharField(max_length=100)  # Increased max_length for city names
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True, null=True)  # Allowing null values
    # age = models.IntegerField()  # Removed redundant age field

    # Internal control
    status = models.CharField(max_length=30, default='active')

    club = models.ForeignKey('Club', related_name='athletes', on_delete=models.CASCADE, null=True, blank=True)  # Linking to Club

    def __str__(self):
        return f"{self.complete_name} ({self.eternal_number})"
    
    class Meta:
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['date_of_birth']),
            models.Index(fields=['gender']),
            models.Index(fields=['nickname']),
            models.Index(fields=['state']),
            models.Index(fields=['country']),
            models.Index(fields=['eternal_number']),
            models.Index(fields=['email']),
            # More? Pictures?
        ]