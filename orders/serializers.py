from rest_framework import serializers
from .models import Order, OrderItem, Payment
from products.models import ProductVariant

class OrderItemSerializer(serializers.ModelSerializer):
    product_variant_id = serializers.IntegerField(write_only=True)
    product_name = serializers.CharField(source='product_variant.product.name', read_only=True)
    amount = serializers.CharField(source='product_variant.amount', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_variant_id', 'product_name', 'amount', 'quantity', 'unit_price']
        read_only_fields = ['unit_price']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'payment_type', 'payment_status', 'transaction_id', 'paid_at']
        read_only_fields = ['payment_status', 'paid_at']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    payment = PaymentSerializer()

    class Meta:
        model = Order
        fields = ['id', 'customer', 'order_date', 'total_amount', 'payment_method', 'order_status', 'created_by', 'items', 'payment']
        read_only_fields = ['customer', 'order_date', 'total_amount', 'order_status', 'created_by', 'payment_method']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        payment_data = validated_data.pop('payment')
        
        request = self.context.get('request')
        user = request.user
        
        # Determine customer (if admin creating for customer vs customer creating)
        customer_id = self.initial_data.get('customer')
        if user.role in ['ADMIN', 'STAFF'] and customer_id:
            customer = user.__class__.objects.get(id=customer_id)
            created_by = user
        else:
            customer = user
            created_by = None
            
        validated_data['customer'] = customer
        validated_data['created_by'] = created_by
        validated_data['payment_method'] = payment_data.get('payment_type')
        
        order = Order.objects.create(**validated_data)
        
        total_amount = 0
        for item_data in items_data:
            variant_id = item_data.pop('product_variant_id')
            variant = ProductVariant.objects.get(id=variant_id)
            quantity = item_data.get('quantity', 1)
            unit_price = variant.price
            
            OrderItem.objects.create(
                order=order,
                product_variant=variant,
                quantity=quantity,
                unit_price=unit_price
            )
            total_amount += (unit_price * quantity)
            
        order.total_amount = total_amount
        order.save()
        
        # Create Payment record
        Payment.objects.create(order=order, **payment_data)
        
        return order
