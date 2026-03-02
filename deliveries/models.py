from django.db import models
from orders.models import Order

class Delivery(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('In Transit', 'In Transit'),
        ('Delivered', 'Delivered'),
    )
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    delivery_partner = models.CharField(max_length=100, blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    delivery_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    delivered_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Delivery for Order #{self.order.id} - {self.delivery_status}"
