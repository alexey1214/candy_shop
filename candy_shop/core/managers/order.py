from django.db import models


class OrderManager(models.Manager):
    def available(self):
        return self.filter(shipment__isnull=True)

    def suitable_for_courier(self, capacity, region_ids, shift_start, shift_end):
        return (self.available()
                    .exclude(weight__gt=capacity)
                    .filter(region__in=region_ids)
                    .filter(delivery_intervals__start__lt=shift_end,
                            delivery_intervals__end__gt=shift_start))
