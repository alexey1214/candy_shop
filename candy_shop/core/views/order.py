from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets, views
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.models import Order
from core.serializers import OrderSerializer, OrdersAssignSerializer, OrderCompleteSerializer


class OrderViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Order.objects.all()
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Order.objects.all()
        order = get_object_or_404(queryset, pk=pk)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = Order.objects.all()
        courier = get_object_or_404(queryset, pk=pk)
        courier.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        if 'data' not in request.data:
            raise ValidationError({'data': 'This field is required.'})

        failed_ids = []
        valid_ids = []

        for order_data in request.data['data']:
            serializer = OrderSerializer(data=order_data)
            if not serializer.is_valid():
                failed_ids.append(order_data.get('order_id', -1))
            else:
                valid_ids.append(order_data.get('order_id', -1))

        if failed_ids:
            raise ValidationError({
                    'validation_error': [{'id': i} for i in failed_ids]})

        serializer = OrderSerializer(data=request.data['data'], many=True)
        serializer.is_valid()
        serializer.save()

        return Response({'orders': [{'id': i} for i in valid_ids]}, status=status.HTTP_201_CREATED)


class OrderAssignView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = OrdersAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderCompleteView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = OrderCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
