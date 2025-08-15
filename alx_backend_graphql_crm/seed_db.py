import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Category
from django.db import transaction

# Clear existing data to prevent duplicates
def clear_db():
    Customer.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    print("Database cleared.")

# Seed the database with sample data
def seed_db():
    with transaction.atomic():
        # Create Categories
        electronics, _ = Category.objects.get_or_create(name='Electronics', description='Electronic gadgets and devices.')
        books, _ = Category.objects.get_or_create(name='Books', description='A collection of books.')

        print("Categories seeded.")

        # Create Products
        Product.objects.create(name='Laptop', description='A powerful laptop.', price=1200.50, stock=10, category=electronics)
        Product.objects.create(name='Smartphone', description='A new smartphone.', price=800.00, stock=25, category=electronics)
        Product.objects.create(name='The Hitchhiker’s Guide to the Galaxy', description='A comic science fiction novel.', price=10.99, stock=100, category=books)

        print("Products seeded.")

        # Create Customers
        Customer.objects.create(name='Alice Smith', email='alice.smith@example.com', phone='1234567890')
        Customer.objects.create(name='Bob Johnson', email='bob.johnson@example.com', phone='0987654321')

        print("Customers seeded.")

if __name__ == '__main__':
    clear_db()
    seed_db()
    print("Database seeding complete.")
