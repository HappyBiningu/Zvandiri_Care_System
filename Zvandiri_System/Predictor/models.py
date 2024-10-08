from datetime import datetime
from django.db import models
from django.utils import timezone

class Patient(models.Model):
    GENDER_CHOICES = (
        (0, 'Female'),
        (1, 'Male'),
    )

    VL_COUNT_CHOICES = (
        (0, 'Yes'),  # Virally suppressed
        (1, 'No'),   # Not virally suppressed
    )

    ATTENDED_CHOICES = (
        (0, 'No'),
        (1, 'Yes'),
    )

    MH_CHOICES = (
        (0, 'No'),
        (1, 'Yes'),
    )

    PREGNANT_CHOICES = (
        (0, 'No'),
        (1, 'Yes'),
    )

    name = models.CharField(max_length=255,default="Unknown")
    vl_count = models.IntegerField(choices=VL_COUNT_CHOICES,default=0)
    attended_last_appointment = models.IntegerField(choices=ATTENDED_CHOICES,default=0)
    gender = models.IntegerField(choices=GENDER_CHOICES,default=0)
    mh = models.IntegerField(choices=MH_CHOICES,default=0)
    breastfeeding = models.IntegerField(choices=ATTENDED_CHOICES, default=0)
    pregnant = models.IntegerField(choices=PREGNANT_CHOICES, default=0)

    def __str__(self):
        return self.name


class PredictionHistory(models.Model):
    patient = models.CharField(max_length=255)  # Store patient name as a string
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], default='Male')
    prediction_text = models.CharField(max_length=255)
    recommendations = models.JSONField(default=list)
    date = models.DateTimeField(default=datetime.now) 
    
   


    def __str__(self):
        return f"Prediction for {self.patient} on {self.date.strftime('%Y-%m-%d')}"






