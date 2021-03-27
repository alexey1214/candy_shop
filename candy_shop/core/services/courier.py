from django.db import transaction, IntegrityError
from django.utils import timezone

from core.models import Courier, Order, Shipment


def _pack_a_bag(courier, filtered_orders):
    bag = {}

    for shift in courier.work_shift_intervals:
        orders = (
                filtered_orders
                .suitable_for_courier(
                    capacity=courier.capacity,
                    region_ids=courier.region_ids,
                    shift_start=shift['start'],
                    shift_end=shift['end'])
                .exclude(id__in=bag.keys())
                .order_by('weight')
                .values_list('id', 'weight'))

        for order_id, order_weight in orders:
            if order_weight + sum(bag.values()) > courier.capacity:
                break
            bag[order_id] = order_weight

    return bag


@transaction.atomic
def assign_orders(courier_id):
    """Assign to the courier maximum number of available orders that'll fit in
    the one's bag given the courier's work regions and work shifts. Return the
    list of order IDs and the assign time.

    If the courier's delivery is in progress, return only undelivered orders.
    """
    courier = Courier.objects.get(id=courier_id)

    # If delivery is in progress, we should return only not (yet) delivered orders
    if courier.active_shipment:
        orders = (Order.objects
                  .assigned_to_courier(courier)
                  .not_delivered_yet()
                  .values_list('id', flat=True))
        return sorted(orders), courier.active_shipment.assign_time

    # No active delivery, so we should create one, using not assigned yet orders
    bag = _pack_a_bag(courier=courier, filtered_orders=Order.objects.not_assigned_yet())
    if bag:
        shipment = Shipment.objects.create(courier=courier, initial_courier_type=courier.type)
        fitting_orders = Order.objects.filter(id__in=bag.keys())
        fitting_orders.update(shipment=shipment)
        shipment.assign_time = timezone.now()
        shipment.save()
        return sorted(bag.keys()), shipment.assign_time

    # No active deliveries, no suitable orders for this courier
    return [], None


@transaction.atomic
def complete_order(order_id, complete_time):
    order = Order.objects.get(id=order_id)

    if not order.complete_time:
        shipment = order.shipment
        if order.shipment.orders.filter(complete_time__isnull=True).count() == 1:
            # This is the last (or the only one) order in the shipment
            shipment.complete_time = complete_time
            shipment.save()
        order.complete_time = complete_time
        order.save()


@transaction.atomic
def edit_courier(courier, courier_type=None, region_ids=None, work_shift_intervals=None):
    try:
        courier.type = courier_type or courier.type
        courier.region_ids = region_ids or courier.region_ids
        courier.work_shift_intervals = work_shift_intervals or courier.work_shift_intervals
        courier.save()

        # Find suitable (for new parameters) orders among assigned but not yet
        # delivered orders and throw out unsuitable or non-fitting into the bag
        # ones
        if courier.active_shipment:
            orders = Order.objects.assigned_to_courier(courier).not_delivered_yet()
            bag = _pack_a_bag(courier=courier, filtered_orders=orders)
            non_fitting_orders = courier.active_shipment.orders.exclude(id__in=bag.keys())
            non_fitting_orders.update(shipment=None)
    except IntegrityError:
        raise
    return courier
