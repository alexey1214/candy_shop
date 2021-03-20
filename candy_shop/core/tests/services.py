from decimal import Decimal

from django.test import TestCase

from core.models import Courier, Order
from core.services import courier as courier_service


class OrdersSuitableForCourierTestCase(TestCase):
    fixtures = ['test_set1']

    @classmethod
    def setUpTestData(cls):
        cls.courier1 = Courier.objects.get(id=1)
        cls.courier3 = Courier.objects.get(id=3)

    def test_courier1(self):
        shift_start, shift_end = self.courier1.work_shift_intervals[0]
        orders = (Order.objects
                  .suitable_for_courier(
                        capacity=self.courier1.capacity,
                        region_ids=self.courier1.region_ids,
                        shift_start=shift_start,
                        shift_end=shift_end))
        self.assertEqual(set(orders.values_list('id', flat=True)), {1, 3})

    def test_courier3(self):
        shift_start, shift_end = self.courier3.work_shift_intervals[1]
        orders = (Order.objects
                  .suitable_for_courier(
                        capacity=self.courier3.capacity,
                        region_ids=self.courier3.region_ids,
                        shift_start=shift_start,
                        shift_end=shift_end))
        self.assertEqual(set(orders.values_list('id', flat=True)), {1, 3})


class AssignOrdersTestCase(TestCase):
    fixtures = ['test_set1']

    @classmethod
    def setUpTestData(cls):
        cls.courier1 = Courier.objects.get(id=1)

    def test_fill_the_bag(self):
        courier = Courier.objects.get(id=1)
        shift_start, shift_end = courier.work_shift_intervals[0]

        bag = {}

        courier_service._fill_the_bag(
                bag=bag, capacity=courier.capacity, region_ids=courier.region_ids,
                shift_start=shift_start, shift_end=shift_end)

        self.assertEqual(bag, {1: Decimal('0.23'), 3: Decimal('0.01')})
