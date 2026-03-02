from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from products.models import Product, ProductVariant
from orders.models import Order

class OrderAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(username='admin', password='password', role='ADMIN')
        self.customer = User.objects.create_user(username='customer', password='password', role='CUSTOMER')
        
        self.product = Product.objects.create(name='Test Product', category='Test', description='Test')
        self.variant = ProductVariant.objects.create(product=self.product, amount='250gm', price=200.00, stock_quantity=10)
        
    def test_create_order(self):
        self.client.force_authenticate(user=self.customer)
        data = {
            "items": [
                {"product_variant_id": self.variant.id, "quantity": 2}
            ],
            "payment": {
                "payment_type": "COD"
            }
        }
        response = self.client.post('/api/orders/', data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.first().total_amount, 400.00)
        
    def test_confirm_order_reduces_stock(self):
        self.client.force_authenticate(user=self.customer)
        data = {"items": [{"product_variant_id": self.variant.id, "quantity": 2}], "payment": {"payment_type": "COD"}}
        response = self.client.post('/api/orders/', data, format='json')
        order_id = response.data['id']
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/orders/{order_id}/confirm/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 8)
        
    def test_cancel_order_restores_stock(self):
        self.test_confirm_order_reduces_stock()
        order = Order.objects.first()
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/orders/{order.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 10)
        self.assertEqual(Order.objects.first().order_status, 'Canceled')
