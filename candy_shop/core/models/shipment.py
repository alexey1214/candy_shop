from django.db import models


class Shipment(models.Model):
    courier = models.ForeignKey(
            'core.Courier', on_delete=models.CASCADE, related_name='shipments')
    assign_time = models.DateTimeField(blank=True, null=True)
    complete_time = models.DateTimeField(blank=True, null=True)
