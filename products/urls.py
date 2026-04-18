# Patch Django's register_converter to handle re-registration gracefully
import django.urls.converters
_original_django_register = django.urls.converters.register_converter

def _safe_register(converter, type_name):
    try:
        _original_django_register(converter, type_name)
    except ValueError:
        pass

django.urls.converters.register_converter = _safe_register

# Also patch DRF's local reference since it imports register_converter directly
import rest_framework.urlpatterns
rest_framework.urlpatterns.register_converter = _safe_register

from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, SupplierViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'', ProductViewSet)

urlpatterns = router.urls