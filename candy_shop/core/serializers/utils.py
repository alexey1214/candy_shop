from datetime import datetime

from rest_framework import serializers


class TimeIntervalSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return f"{instance['start']:%H:%M}-{instance['end']:%H:%M}"

    def to_internal_value(self, data):
        try:
            start, end = (datetime.strptime(s, '%H:%M') for s in data.split('-'))
        except Exception:
            raise serializers.ValidationError(f'Incorrect format: "{data}".')
        return {'start': start, 'end': end}
