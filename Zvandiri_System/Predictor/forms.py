from django import forms
from .models import Patient

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'vl_count', 'attended_last_appointment', 'gender', 'mh', 'breastfeeding', 'pregnant']
        
        
        
from .models import PredictionHistory

class PatientForm(forms.ModelForm):
    class Meta:
        model = PredictionHistory
        fields = ['patient', 'gender',  'prediction_text']  # Add any other fields you want to edit
