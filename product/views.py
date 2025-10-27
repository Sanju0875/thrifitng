from django.shortcuts import render, redirect, get_object_or_404  # REMOVE THIS LINE
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

    return render(request, 'shop/index.html', {
        'products_object': products,
        'total_quantity': total_quantity,
    })

@login_required(login_url='login')  # Redirects to login if not authenticated
def checkout_view(request):
    # Your checkout logic here
    return render(request, 'shop/checkout.html')

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
    return render(request, 'shop/product_detail.html', {'product': product, 'total_quantity': total_quantity })

def signup_view(request):
    # your signup logic here or just render signup template for now
    return render(request, 'shop/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Redirect to next page if available, else order_summary
            next_url = request.GET.get('next') or 'order_summary'
            return redirect('order_summary')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})

    return render(request, 'order_summary.html')

def order_summary(request):
    return render(request, 'shop/order_summary.html')

@require_POST
def add_to_cart(request, pk):
    product = get_object_or_404(Products, pk=pk)  # ⬅ FIXED
    cart = request.session.get('cart', {})

    if str(pk) in cart:  # ⬅ FIXED
        cart[str(pk)] += 1
    else:
        cart[str(pk)] = 1

    request.session['cart'] = cart
    return redirect('cart')

# Update quantity
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


def cart_view(request):
    cart = request.session.get('cart', {})  # Get cart from session (dict: product_id -> quantity)
    cart_items = []  # List to store each item detail

    total_quantity = 0
    total_price = 0

    for product_id, quantity in cart.items():
        product = Products.objects.get(pk=product_id)  # ✅ FIXED
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

