from django.db import models


class Order(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2)  # In kilograms
    region = models.ForeignKey(
            'core.Region', on_delete=models.CASCADE, related_name='orders')

    def __str__(self):
        return f'{self.id}'


class OrderDeliveryInterval(models.Model):
    order = models.ForeignKey(
            'core.Order', on_delete=models.CASCADE, related_name='delivery_intervals')
    start = models.TimeField()
    end = models.TimeField()

    def __str__(self):
        return f'{self.id} ({self.order}, {self.start:%H:%M}-{self.end:%H:%M})'
