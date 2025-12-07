from django.contrib import admin
from .models import Product, CustomerInterested, CartItem, Transaction, Order

admin.site.register(Product)
admin.site.register(CustomerInterested)
admin.site.register(CartItem)
admin.site.register(Transaction)
admin.site.register(Order)
