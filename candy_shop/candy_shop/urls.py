"""candy_shop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from rest_framework import routers
from core import views


class OptionalSlashRouter(routers.DefaultRouter):
    def __init__(self):
        super().__init__()
        self.trailing_slash = '/?'


router = OptionalSlashRouter()
router.register(r'courier_types', views.CourierTypeViewSet)
router.register(r'couriers', views.CourierViewSet, basename='Courier')
router.register(r'orders', views.OrderViewSet, basename='Order')

urlpatterns = [
    path('orders/assign', views.OrderAssignView.as_view()),
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]
