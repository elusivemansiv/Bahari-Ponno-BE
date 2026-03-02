from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    description = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=(('Active', 'Active'), ('Inactive', 'Inactive')), default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    amount = models.CharField(max_length=100, help_text="e.g., 250gm, 500gm")
    price = models.DecimalField(max_length=10, max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.amount}"
