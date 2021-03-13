from django.db import models


class CourierType(models.Model):
    code = models.CharField(primary_key=True, max_length=10)
    capacity = models.DecimalField(max_digits=6, decimal_places=2)  # In kilograms


class Courier(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    type = models.ForeignKey('core.CourierType', on_delete=models.CASCADE)


class CourierWorkShift(models.Model):
    courier = models.ForeignKey('core.Courier', on_delete=models.CASCADE)
    start = models.TimeField()
    end = models.TimeField()


class CourierRegion(models.Model):
    courier = models.ForeignKey('core.Courier', on_delete=models.CASCADE)
    region = models.ForeignKey('core.Region', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['courier', 'region'], name='unique_courier_region')
        ]
