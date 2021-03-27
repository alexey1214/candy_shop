from collections import defaultdict

from django.db import transaction, IntegrityError
from django.db.models import Count
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


def _get_durations_and_regions(shipment):
    result = []

    complete_times_and_regions = (
            shipment.orders
            .order_by('complete_time')
            .values_list('complete_time', 'region'))

    for i, (complete_time, region) in enumerate(complete_times_and_regions):
        if i > 0:
            prev_complete_time, _ = complete_times_and_regions[i - 1]
            duration = complete_time - prev_complete_time
        else:
            duration = complete_time - shipment.assign_time
        result.append((int(duration.total_seconds()), region))

    return result


def calculate_rating(courier):
    if courier.completed_shipments.exists():
        regions_and_durations = defaultdict(list)

        for shipment in courier.completed_shipments:
            durations_and_regions = _get_durations_and_regions(shipment=shipment)
            for d, r in durations_and_regions:
                regions_and_durations[r].append(d)

        avg_durations = [sum(ds) / len(ds) for ds in regions_and_durations.values()]

        if avg_durations:
            t = min(avg_durations)
            rating = (60 * 60 - min(t, 60 * 60)) / (60 * 60) * 5
            return round(rating, 2)

    return None


def calculate_earnings(courier):
    def get_coefficient(courier_type_id):
        if courier_type_id == 'foot':
            return 2
        elif courier_type_id == 'bike':
            return 5
        elif courier_type_id == 'car':
            return 9
        return 0

    if courier.completed_shipments.exists():
        types_and_counts = (
                courier.completed_shipments
                .values_list('initial_courier_type')
                .annotate(count=Count('initial_courier_type')))
        return 500 * sum(get_coefficient(t) * c for t, c in types_and_counts)

    return None
