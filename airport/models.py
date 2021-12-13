from django.db import models

class Country(models.Model):
    country_code = models.CharField(primary_key=True, max_length=2, null=False,default = 'US')
    country_name = models.CharField(max_length=100, null=False)
    def __str__(self):
        return self.country_name

class Zone(models.Model):
    zone_id = models.IntegerField(primary_key=True, null=False)
    country_code = models.ForeignKey(Country,default = 00, on_delete=models.SET_DEFAULT)
    zone_name = models.CharField(max_length=35, null=False,unique=True)
    def __str__(self):
        return self.zone_name

class Timezone(models.Model):
    zone_id = models.ForeignKey(Zone,default = 00, on_delete=models.SET_DEFAULT)
    abbreviation = models.CharField(max_length=6, null=False)
    time_start = models.BigIntegerField(null=False)
    gmt_offset = models.IntegerField(null = False)
    dst = models.CharField(max_length=1, null=False)
    def __str__(self):
        return self.abbreviation
class Airport(models.Model):
    icao = models.CharField(primary_key=True, max_length=4)
    iata = models.CharField(max_length=4,blank=True,null=True)
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=200,blank=True)
    state = models.CharField(max_length=200,blank=True)
    country = models.CharField(max_length=2,blank=True)
    elevation = models.SmallIntegerField(blank=True)
    lat = models.DecimalField(max_digits=14,decimal_places=11)
    long = models.DecimalField(max_digits=14,decimal_places=11)
    zone_name = models.ForeignKey(Zone, to_field='zone_name',db_column='zone_name', default = 'Blank', on_delete=models.SET_DEFAULT,blank=True,null=True)
    date_added = models.DateTimeField(blank=True)
    date_edited = models.DateTimeField(blank=True)

    def __str__(self):
        return self.icao

