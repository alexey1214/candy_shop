from django.db import models


class Region(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)

    def __str__(self):
        return f'{self.id}'
