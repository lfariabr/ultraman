from django.db import models
from athletes.models.athlete import Athlete

class Document(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('contract', 'Contract'),
        ('residency_proof', 'Residency Proof'),
        ('rg', 'RG'),
        ('cnh', 'CNH'),
        # Add more if necessary
    ]
    athlete = models.ForeignKey(Athlete, related_name='documents', on_delete=models.CASCADE)
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_document_type_display()} for {self.athlete.complete_name}"