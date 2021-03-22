from decimal import Decimal

from rest_framework import serializers

from core.models import Order, Courier
from core.serializers.utils import TimeIntervalSerializer
from core.services.courier import assign_orders


class OrderSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(source='id', min_value=1)
    weight = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=Decimal('0.01'), coerce_to_string=False)
    region = serializers.IntegerField(source='region.id', min_value=1)
    delivery_hours = serializers.ListSerializer(child=TimeIntervalSerializer(), write_only=True, allow_empty=False)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        intervals = instance.delivery_intervals.order_by('start').values('start', 'end')
        ret['delivery_hours'] = TimeIntervalSerializer(intervals, many=True).data
        return ret

    def create(self, validated_data):
        """validated_data = {
            'id': 5,
            'weight': Decimal('7.60'),
            'region': 1,
            'delivery_hours': [
                {
                    'start': datetime.datetime(1900, 1, 1, 11, 25),
                    'end': datetime.datetime(1900, 1, 1, 13, 20)
                },
            ]}
        """
        order_id = validated_data['id']
        order, created = Order.objects.get_or_create(
                id=order_id,
                defaults={'weight': validated_data['weight'],
                          'region_id': validated_data['region']['id']})
        if not created:
            raise serializers.ValidationError(f'Order({order_id}) already exists.')

        for interval in validated_data['delivery_hours']:
            order.delivery_intervals.get_or_create(start=interval['start'], end=interval['end'])

        return order


class OrderResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class OrdersAssignSerializer(serializers.Serializer):
    courier_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Courier.objects.all())
    orders = OrderResponseSerializer(many=True, read_only=True)
    assign_time = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        order_ids, assign_time = assign_orders(courier_id=validated_data['courier_id'].id)
        return {'orders': [{'id': i} for i in order_ids], 'assign_time': assign_time}
