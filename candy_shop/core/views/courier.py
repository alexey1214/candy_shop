from rest_framework import viewsets

from core.models import CourierType, Courier
from core.serializers import CourierTypeSerializer, CourierSerializer


class CourierTypeViewSet(viewsets.ModelViewSet):
    queryset = CourierType.objects.all()
    serializer_class = CourierTypeSerializer


class CourierViewSet(viewsets.ModelViewSet):
    queryset = Courier.objects.all()
    serializer_class = CourierSerializer
