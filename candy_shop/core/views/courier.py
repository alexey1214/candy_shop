from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets, views
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.models import CourierType, Courier
from core.serializers import (
        CourierTypeSerializer, CourierSerializer, CourierEditSerializer,
        CourierStatsSerializer,)


class CourierTypeViewSet(viewsets.ModelViewSet):
    queryset = CourierType.objects.all()
    serializer_class = CourierTypeSerializer


class CourierViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Courier.objects.all()
        serializer = CourierSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Courier.objects.all()
        courier = get_object_or_404(queryset, pk=pk)
        serializer = CourierSerializer(courier)
        return Response(serializer.data)

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = Courier.objects.all()
        courier = get_object_or_404(queryset, pk=pk)
        courier.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        if 'data' not in request.data:
            raise ValidationError({'data': 'This field is required.'})

        failed_ids = []
        valid_ids = []

        for courier_data in request.data['data']:
            serializer = CourierSerializer(data=courier_data)
            if not serializer.is_valid():
                failed_ids.append(courier_data.get('courier_id', -1))
            else:
                valid_ids.append(courier_data.get('courier_id', -1))

        if failed_ids:
            raise ValidationError({
                    'validation_error': {
                        'couriers': [{'id': i} for i in failed_ids]}})

        serializer = CourierSerializer(data=request.data['data'], many=True)
        serializer.is_valid()
        serializer.save()

        return Response({'couriers': [{'id': i} for i in valid_ids]}, status=status.HTTP_201_CREATED)


class CourierDetailView(views.APIView):
    def get(self, request, pk):
        courier = get_object_or_404(Courier.objects.all(), pk=pk)
        serializer = CourierStatsSerializer(courier)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        try:
            courier = Courier.objects.get(id=self.kwargs['pk'])
        except ObjectDoesNotExist:
            raise views.exceptions.ValidationError({'courier_id': 'Courier does not exist.'})
        serializer = CourierEditSerializer(courier, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
