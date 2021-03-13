from django.db import models


class Order(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2)  # In kilograms
    region = models.ForeignKey('core.Region', on_delete=models.CASCADE)


class OrderDeliveryInterval(models.Model):
    order = models.ForeignKey('core.Order', on_delete=models.CASCADE)
    start = models.TimeField()
    end = models.TimeField()
