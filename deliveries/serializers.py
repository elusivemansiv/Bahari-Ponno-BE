from rest_framework import serializers
from .models import Delivery

class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = ['id', 'order', 'delivery_partner', 'tracking_number', 'delivery_status', 'delivered_at']
        read_only_fields = ['order']
