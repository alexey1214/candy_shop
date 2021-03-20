from django.db import transaction
from django.utils import timezone

from core.models import Courier, Order, Shipment


def _fill_the_bag(bag, capacity, region_ids, shift_start, shift_end):
    orders = (
            Order.objects.suitable_for_courier(
                capacity=capacity,
                region_ids=region_ids,
                shift_start=shift_start,
                shift_end=shift_end)
            .exclude(id__in=bag.keys())
            .order_by('weight')
            .values_list('id', 'weight'))

    for order_id, order_weight in orders:
        if order_weight + sum(bag.values()) > capacity:
            break
        bag[order_id] = order_weight


@transaction.atomic
def assign_orders(courier_id):
    """Assign to the courier maximum number of available orders that'll fit in
    the one's bag given the courier's work regions and work shifts. Return the
    list of order IDs and the assign time.

    If the courier's delivery is in progress, return only undelivered orders.
    """
    courier = Courier.objects.get(id=courier_id)

    # If delivery is in progress, we should return only not (yet) delivered orders
    active_shipment = courier.shipments.filter(complete_time__isnull=True).last()
    if active_shipment:
        undelivered_orders = (
                active_shipment.orders
                .filter(complete_time__isnull=True)
                .values_list('id', flat=True))
        return sorted(undelivered_orders), active_shipment.assign_time

    # No active delivery, so we should create one
    bag = {}
    for shift_start, shift_end in courier.work_shift_intervals:
        _fill_the_bag(bag, courier.capacity, courier.region_ids, shift_start, shift_end)

    if bag:
        order_ids = list(bag.keys())
        shipment = Shipment.objects.create(courier=courier)
        Order.objects.filter(id__in=order_ids).update(shipment=shipment)
        shipment.assign_time = timezone.now()
        shipment.save()
        return sorted(bag.keys()), shipment.assign_time

    # No active deliveries, no suitable orders for this courier
    return [], None
