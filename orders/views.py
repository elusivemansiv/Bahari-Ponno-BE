from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Order, OrderItem
from .serializers import OrderSerializer
from products.models import ProductVariant

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'STAFF']:
            return Order.objects.all()
        return Order.objects.filter(customer=user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def confirm(self, request, pk=None):
        order = self.get_object()
        
        if request.user.role not in ['ADMIN', 'STAFF']:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
            
        if order.order_status != 'Pending':
            return Response({"detail": "Order can only be confirmed if it is pending."}, status=status.HTTP_400_BAD_REQUEST)
            
        with transaction.atomic():
            order.order_status = 'Confirmed'
            order.save()
            
            # Reduce stock
            for item in order.items.all():
                variant = item.product_variant
                if variant:
                    if variant.stock_quantity < item.quantity:
                        return Response({"detail": f"Not enough stock for {variant.product.name} ({variant.amount})"}, status=status.HTTP_400_BAD_REQUEST)
                    variant.stock_quantity -= item.quantity
                    variant.save()
                    
        return Response({"status": "Order confirmed and stock reduced."})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, pk=None):
        order = self.get_object()
        
        if request.user.role not in ['ADMIN', 'STAFF']:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
            
        if order.order_status == 'Canceled':
            return Response({"detail": "Order is already canceled."}, status=status.HTTP_400_BAD_REQUEST)
            
        # If it was confirmed, we need to restore stock
        was_confirmed = order.order_status in ['Confirmed', 'Shipped', 'Delivered']
        
        with transaction.atomic():
            order.order_status = 'Canceled'
            order.save()
            
            if was_confirmed:
                # Restore stock
                for item in order.items.all():
                    variant = item.product_variant
                    if variant:
                        variant.stock_quantity += item.quantity
                        variant.save()
                        
        return Response({"status": "Order canceled and stock restored if it was previously confirmed."})

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def update_payment(self, request, pk=None):
        order = self.get_object()
        
        if request.user.role not in ['ADMIN', 'STAFF']:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
            
        if not hasattr(order, 'payment'):
            return Response({"detail": "No payment record found for this order."}, status=status.HTTP_404_NOT_FOUND)
            
        payment = order.payment
        payment_status = request.data.get('payment_status')
        transaction_id = request.data.get('transaction_id')
        
        if payment_status:
            payment.payment_status = payment_status
        if transaction_id:
            payment.transaction_id = transaction_id
            
        if payment_status == 'Paid' and not payment.paid_at:
            from django.utils import timezone
            payment.paid_at = timezone.now()
            
        payment.save()
        return Response({"status": "Payment updated successfully."})
