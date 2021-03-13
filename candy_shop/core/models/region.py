from django.db import models


class Region(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
