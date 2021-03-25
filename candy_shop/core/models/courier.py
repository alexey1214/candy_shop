from django.db import models, transaction

from core.models import Region


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

    @property
    def capacity(self):
        return self.type.capacity

    @property
    def region_ids(self):
        return self.courier_regions.order_by('region').values_list('region', flat=True)

    @region_ids.setter
    @transaction.atomic
    def region_ids(self, ids):
        if set(ids) != set(self.courier_regions.values_list('region', flat=True)):
            self.courier_regions.all().delete()
            for region_id in ids:
                region, created = Region.objects.get_or_create(id=region_id)
                region.courier_regions.create(courier_id=self.id)

    @property
    def work_shift_intervals(self):
        return self.work_shifts.order_by('start').values('start', 'end')

    @work_shift_intervals.setter
    @transaction.atomic
    def work_shift_intervals(self, intervals):
        new_intervals = sorted(intervals, key=lambda i: i['start'])
        old_intervals = sorted(self.work_shift_intervals, key=lambda i: i['start'])
        if new_intervals != old_intervals:
            self.work_shifts.all().delete()
            for interval in new_intervals:
                self.work_shifts.get_or_create(start=interval['start'], end=interval['end'])

    @property
    def active_shipment(self):
        return self.shipments.filter(complete_time__isnull=True).last()


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
