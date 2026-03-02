from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductVariantViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'variants', ProductVariantViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
