# Generated by Django 5.1.1 on 2024-10-03 10:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Predictor', '0009_patient_date_predictionhistory_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='patient',
            old_name='date',
            new_name='date_added',
        ),
    ]
