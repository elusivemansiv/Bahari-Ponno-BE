from django.contrib import admin
from .models import Delivery

class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'delivery_partner', 'delivery_status', 'tracking_number')
    list_filter = ('delivery_status', 'delivery_partner')

admin.site.register(Delivery, DeliveryAdmin)
