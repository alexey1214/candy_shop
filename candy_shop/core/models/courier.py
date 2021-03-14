from django.db import models


class CourierType(models.Model):
    code = models.CharField(primary_key=True, max_length=10)
    capacity = models.DecimalField(max_digits=6, decimal_places=2)  # In kilograms

    def __str__(self):
        return f'{self.code}'


class Courier(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    type = models.ForeignKey(
            'core.CourierType', on_delete=models.CASCADE, related_name='couriers')

    def __str__(self):
        return f'{self.id}'


class CourierWorkShift(models.Model):
    courier = models.ForeignKey(
            'core.Courier', on_delete=models.CASCADE, related_name='work_shifts')
    start = models.TimeField()
    end = models.TimeField()

    def __str__(self):
        return f'{self.id} ({self.courier}, {self.start:%H:%M}-{self.end:%H:%M})'


class CourierRegion(models.Model):
    courier = models.ForeignKey(
            'core.Courier', on_delete=models.CASCADE, related_name='courier_regions')
    region = models.ForeignKey(
            'core.Region', on_delete=models.CASCADE, related_name='courier_regions')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['courier', 'region'], name='unique_courier_region')
        ]

    def __str__(self):
        return f'{self.id} ({self.courier}, {self.region})'
