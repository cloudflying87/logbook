# Generated by Django 3.2.7 on 2022-05-30 15:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logbook', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flighttime',
            name='typeacft',
        ),
    ]
