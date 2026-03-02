from rest_framework import viewsets
from .models import Product, ProductVariant
from .serializers import ProductSerializer, ProductVariantSerializer
from users.permissions import IsAdminUserOrReadOnly, IsAdminUser

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUserOrReadOnly]

class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAdminUser]
    
    def perform_create(self, serializer):
        product_id = self.request.data.get('product')
        product = Product.objects.get(id=product_id)
        serializer.save(product=product)
