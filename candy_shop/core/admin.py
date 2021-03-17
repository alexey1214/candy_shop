from django.contrib import admin

from .models import (
        CourierType, Courier, CourierWorkShift, CourierRegion, Order,
        OrderDeliveryInterval, Region)


@admin.register(CourierType)
class CourierTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'capacity']


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    pass


class CourierRegionInline(admin.TabularInline):
    model = CourierRegion
    extra = 0


class CourierWorkShiftInline(admin.TabularInline):
    model = CourierWorkShift
    extra = 0


@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'regions', 'work_shifts']
    inlines = [CourierRegionInline, CourierWorkShiftInline]

    @staticmethod
    def regions(obj):
        return list(obj.courier_regions.values_list('region', flat=True))

    @staticmethod
    def work_shifts(obj):
        shifts_qs = obj.work_shifts.values_list('start', 'end')
        return list(map(lambda s: f'{s[0]:%H:%M}-{s[1]:%H:%M}', shifts_qs))


class OrderDeliveryIntervalInline(admin.TabularInline):
    model = OrderDeliveryInterval
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'weight', 'region', 'delivery_intervals']
    inlines = [OrderDeliveryIntervalInline]

    @staticmethod
    def delivery_intervals(obj):
        intervals_qs = obj.delivery_intervals.values_list('start', 'end')
        return list(map(lambda i: f'{i[0]:%H:%M}-{i[1]:%H:%M}', intervals_qs))
