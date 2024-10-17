from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100, null=True)
    telegram_id = models.IntegerField(unique=True)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{User.name}"