from rest_framework import serializers

from core.models import CourierType, Courier, Region
from core.serializers.utils import TimeIntervalSerializer
from core.services.courier import edit_courier


class CourierTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourierType
        fields = ['url', 'code', 'capacity']


class CourierSerializer(serializers.Serializer):
    courier_id = serializers.IntegerField(source='id', min_value=1)
    courier_type = serializers.PrimaryKeyRelatedField(source='type', queryset=CourierType.objects.all())
    regions = serializers.ListSerializer(child=serializers.IntegerField(min_value=1), write_only=True, allow_empty=False)
    working_hours = serializers.ListSerializer(child=TimeIntervalSerializer(), write_only=True, allow_empty=False)

    class Meta:
        model = Courier
        fields = ['courier_id', 'courier_type', 'regions', 'working_hours']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['regions'] = instance.region_ids
        shifts = instance.work_shifts.order_by('start').values('start', 'end')
        ret['working_hours'] = TimeIntervalSerializer(shifts, many=True).data
        return ret

    def create(self, validated_data):
        """validated_data = {
            'id': 4,
            'type': <CourierType: foot>,
            'regions': [1, 9],
            'working_hours': [
                {
                    'start': datetime.datetime(1900, 1, 1, 10, 30),
                    'end': datetime.datetime(1900, 1, 1, 12, 20)
                },
            ]}
        """
        courier_id = validated_data['id']
        courier, created = Courier.objects.get_or_create(
                id=courier_id, defaults={'type': validated_data['type']})
        if not created:
            raise serializers.ValidationError(f'Courier({courier_id}) already exists.')

        for region_id in validated_data['regions']:
            region, created = Region.objects.get_or_create(id=region_id)
            region.courier_regions.create(courier_id=courier_id)

        for shift in validated_data['working_hours']:
            courier.work_shifts.get_or_create(start=shift['start'], end=shift['end'])

        return courier


class CourierEditSerializer(serializers.Serializer):
    courier_id = serializers.PrimaryKeyRelatedField(source='id', queryset=Courier.objects.all())
    courier_type = serializers.PrimaryKeyRelatedField(source='type', queryset=CourierType.objects.all())
    regions = serializers.ListSerializer(source='region_ids', child=serializers.IntegerField(min_value=1))
    working_hours = serializers.ListSerializer(source='work_shift_intervals', child=TimeIntervalSerializer())

    def update(self, instance, validated_data):
        return edit_courier(
                courier=instance,
                courier_type=validated_data.get('type'),
                region_ids=validated_data.get('region_ids'),
                work_shift_intervals=validated_data.get('work_shift_intervals'))
