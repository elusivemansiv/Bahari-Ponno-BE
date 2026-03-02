from django.contrib import admin
from .models import Product, ProductVariant

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductVariantInline]
    list_display = ('name', 'category', 'status', 'created_at')
    list_filter = ('status', 'category')

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariant)
