from django.db import models


class OrderQueryset(models.QuerySet):
    def not_assigned_yet(self):
        return self.filter(shipment__isnull=True)

    def not_delivered_yet(self):
        return self.filter(complete_time__isnull=True)

    def assigned_to_courier(self, courier):
        return self.filter(shipment__courier=courier)

    def suitable_for_courier(self, capacity, region_ids, shift_start, shift_end):
        return (self.exclude(weight__gt=capacity)
                    .filter(region__in=region_ids)
                    .filter(delivery_intervals__start__lt=shift_end,
                            delivery_intervals__end__gt=shift_start))
