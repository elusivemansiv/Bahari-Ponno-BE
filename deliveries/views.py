from rest_framework import viewsets, permissions
from .models import Delivery
from .serializers import DeliverySerializer

class IsStaffOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in ['ADMIN', 'STAFF'])

class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsStaffOrAdmin]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'STAFF']:
            return Delivery.objects.all()
        # Customers can only see their own deliveries
        return Delivery.objects.filter(order__customer=user)
