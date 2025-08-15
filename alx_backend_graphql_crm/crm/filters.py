import django_filters
from .models import Customer, Product, Order

class CustomerFilter(django_filters.FilterSet):
    class Meta:
        model = Customer
        fields = {
            'name': ['icontains'],
            'email': ['exact'],
            'phone': ['exact']
        }

class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            'name': ['icontains'],
            'price': ['lt', 'gt'],
            'stock': ['lt', 'gt']
        }

class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = Order
        fields = {
            'order_date': ['gt', 'lt'],
            'total_amount': ['lt', 'gt']
        }