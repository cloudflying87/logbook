# Generated by Django 3.2.7 on 2022-08-01 02:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logbook', '0003_auto_20220801_0215'),
    ]

    operations = [
        migrations.AddField(
            model_name='flighttime',
            name='rotationid',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
