from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
class ItemBase(models.Model):
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        abstract = True

    @property
    def subtotal(self):
        return self.quantity * self.price



class Product(models.Model):
    title = models.CharField(max_length=200)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return self.title


class CartItem(ItemBase):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')

    def __str__(self):
        return f"{self.product.title} ({self.quantity}) in {self.user.username}'s cart"


class CustomerInterested(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderFormInfo(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='billing_info')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Nepal')
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Billing info for Order #{self.order.id}"


class OrderItem(ItemBase):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')

    def __str__(self):
        return f"{self.quantity} x {self.product.title} in Order #{self.order.id}"


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed')
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.transaction_id} for Order #{self.order.id}"
