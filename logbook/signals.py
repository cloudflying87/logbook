from django.db.models.signals import pre_save
from django.dispatch import receiver
from logbook.models import FlightTime
import user

@receiver(pre_save, sender=FlightTime)
def testreciever(sender,instance,**kwargs):
    print('test222')
    print(user)