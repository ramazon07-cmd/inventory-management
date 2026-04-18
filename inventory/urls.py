# Patch Django's register_converter to handle re-registration gracefully
import django.urls.converters
_original_django_register = django.urls.converters.register_converter

def _safe_register(converter, type_name):
    try:
        _original_django_register(converter, type_name)
    except ValueError:
        pass

django.urls.converters.register_converter = _safe_register

import rest_framework.urlpatterns
rest_framework.urlpatterns.register_converter = _safe_register

from rest_framework.routers import DefaultRouter
from .views import StockMovementViewSet

router = DefaultRouter()
router.register(r'', StockMovementViewSet, basename='stock')

urlpatterns = router.urls