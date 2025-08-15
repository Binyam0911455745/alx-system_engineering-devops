import graphene
from graphene_django.types import DjangoObjectType
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Customer, Product, Order, OrderItem, Category
from datetime import datetime

# Define your DjangoObjectType classes first
# ----------------------------------------------------------------------------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "orders")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "description", "price", "stock", "image", "category")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "order_date", "total_amount")

class OrderItemType(DjangoObjectType):
    class Meta:
        model = OrderItem
        fields = ("id", "order", "product")

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ("id", "name", "description", "products")
# ----------------------------------------------------------------------------------


# Define the Input and Mutation classes
# ----------------------------------------------------------------------------------
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)
    
    customer = graphene.Field(CustomerType)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, input):
        if Customer.objects.filter(email=input.email).exists():
            raise ValidationError("Email already exists.")
        
        customer = Customer.objects.create(**input)
        return CreateCustomer(customer=customer, message="Customer created successfully.")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, customers):
        created_customers = []
        errors = []

        with transaction.atomic():
            for customer_data in customers:
                email = customer_data.email
                if Customer.objects.filter(email=email).exists():
                    errors.append(f"Customer with email '{email}' already exists.")
                    continue

                if customer_data.phone and not customer_data.phone.isdigit():
                    errors.append(f"Invalid phone number for '{email}'.")
                    continue
                
                try:
                    customer = Customer.objects.create(**customer_data)
                    created_customers.append(customer)
                except ValidationError as e:
                    errors.append(f"Validation error for '{email}': {str(e)}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)
    
    product = graphene.Field(ProductType)

    @staticmethod
    def mutate(root, info, input):
        if input.price <= 0:
            raise ValidationError("Price must be a positive number.")
        if input.stock and input.stock < 0:
            raise ValidationError("Stock cannot be a negative number.")
        
        product = Product.objects.create(**input)
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)
    
    order = graphene.Field(OrderType)

    @staticmethod
    def mutate(root, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            raise ValidationError(f"Invalid customer ID: {input.customer_id}")

        products = []
        total_amount = 0

        for product_id in input.product_ids:
            try:
                product = Product.objects.get(pk=product_id)
                products.append(product)
                total_amount += product.price
            except Product.DoesNotExist:
                raise ValidationError(f"Invalid product ID: {product_id}")

        if not products:
            raise ValidationError("An order must have at least one product.")
        
        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=input.order_date if input.order_date else datetime.now()
        )
        order.products.set(products)

        return CreateOrder(order=order)

# ----------------------------------------------------------------------------------

# Define the main Query and Mutation classes for the crm app
# ----------------------------------------------------------------------------------
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)
    order_items = graphene.List(OrderItemType)
    categories = graphene.List(CategoryType)

    def resolve_customers(self, info):
        return Customer.objects.all()

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_orders(self, info):
        return Order.objects.all()

    def resolve_order_items(self, info):
        return OrderItem.objects.all()

    def resolve_categories(self, info):
        return Category.objects.all()

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
# ----------------------------------------------------------------------------------