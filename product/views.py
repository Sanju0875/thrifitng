from django.shortcuts import render, redirect, get_object_or_404
from .models import Products
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.db.models import Q
from django.contrib.auth.models import User
from .forms import SignupForm
from django.views.decorators.http import require_POST
from django.contrib import messages
import random
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .models import CartItem
import pickle
from django.contrib.auth import logout
import os
from django.conf import settings
from .models import CustomerInterested
from .utils import get_recommendations


def home(request):
    cart = request.session.get('cart', {})  # Get cart from session
    total_quantity = sum(cart.values())  # Calculate total quantity in cart

    query = request.GET.get('q')
    if query:
        products = Products.objects.filter(title__icontains=query)
        
    else:
        products = Products.objects.all()
        
        new_arrivals = Products.objects.order_by('-id')[:6]

    return render(request, 'shop/home.html', {
        'products_object': products,
        'new_arrivals': new_arrivals,
        'total_quantity': total_quantity,
        'query': query
    })


def index(request):
    cart = request.session.get('cart', {})
    total_quantity = sum(cart.values())

    query = request.GET.get('q')
    if query:
        products = Products.objects.filter(title__icontains=query)
    else:
        products = Products.objects.all()

    # Get recommendations only for logged-in users
    recommended_products = []   
    if request.user.is_authenticated:
        # Get last 5 products viewed by user
        last_viewed = CustomerInterested.objects.filter(user=request.user).order_by('-viewed_at')[:5]
        last_viewed_titles = [p.product for p in last_viewed]

        if last_viewed_titles:
            recommended_products = get_recommendations(last_viewed_titles, top_n=5)

    return render(request, 'shop/index.html', {
        'products_object': products,
        'recommended_products': recommended_products,
        'total_quantity': total_quantity,
    })

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.subtotal for item in cart_items)
    total_quantity = sum(item.quantity for item in cart_items)

    if request.method == 'POST':
        # when user clicks Place Order
        CartItem.objects.filter(user=request.user).delete()
        return render(request, 'shop/order_success.html', {'total_price': total_price})

    return render(request, 'shop/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_quantity': total_quantity
    })

def search_products(request):
    query = request.GET.get('q')
    if query:
        products = Products.objects.filter(title__icontains=query)
    else:
        products = Products.objects.all()
    return render(request, 'search.html', {'products': products, 'query': query})

def product_detail(request, pk):
    product = get_object_or_404(Products, pk=pk)
    cart = request.session.get('cart', {})
    total_quantity = sum(cart.values())

    if request.user.is_authenticated:
        CustomerInterested.objects.get_or_create(user=request.user, product=product)

    return render(request, 'shop/product_detail.html', {'product': product, 'total_quantity': total_quantity })

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()
        email = request.POST.get('email', '').strip()

        # Check if username exists
        if User.objects.filter(username=username).exists():
            return render(request, 'shop/signup.html', {'error': 'Username already exists'})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        login(request, user)

        return redirect('order_summary')

    return render(request, 'shop/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('order_summary')  # Correct redirect
        else:
            return render(request, 'shop/login.html', {'error': 'Invalid credentials'})

    return render(request, 'shop/login.html')

@login_required
def order_summary(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.subtotal for item in cart_items)
    total_quantity = sum(item.quantity for item in cart_items)
    return render(request, 'shop/order_summary.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_quantity': total_quantity
    })

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Products, pk=pk)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    messages.success(request, f"{product.title} added to your cart!")
    return redirect('shop/cart.html') 

@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.subtotal for item in cart_items)
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

def update_cart(request, pk):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        if quantity > 0:
            cart[str(pk)] = quantity
        else:
            cart.pop(str(pk), None)
        request.session['cart'] = cart
    return redirect('cart')

def process_order(request):
    if request.method == "POST":
        return redirect('order_summary')
    else:
        return redirect('checkout')

def cart_view(request):
    cart = request.session.get('cart', {})  
    cart_items = []  

    total_quantity = 0
    total_price = 0

    for product_id, quantity in cart.items():
        product = Products.objects.get(pk=product_id)  
        total_quantity += quantity
        total_price += product.price * quantity
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': product.price * quantity
        })

    context = {
        'cart_items': cart_items,
        'total_quantity': total_quantity,
        'total_price': total_price,
    }
    return render(request, 'shop/cart.html', context)

def increase_quantity(request, pk):  # ⬅ FIXED
    cart = request.session.get('cart', {})
    cart[str(pk)] = cart.get(str(pk), 0) + 1
    request.session['cart'] = cart
    return redirect('cart')

def decrease_quantity(request, pk):  # ⬅ FIXED
    cart = request.session.get('cart', {})
    if str(pk) in cart:
        if cart[str(pk)] > 1:
            cart[str(pk)] -= 1
        else:
            del cart[str(pk)]
    request.session['cart'] = cart
    return redirect('cart')


def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    cart.pop(str(pk), None)
    request.session['cart'] = cart
    return redirect('cart')