from django.shortcuts import render, redirect
from .models import Products
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.db.models import Q
from django.contrib.auth.models import User
from .forms import SignupForm

import random

#  Create your views here.

def home(request):
    return render(request, 'shop/home.html')

def index(request):
    products = Products.objects.all()
    return render(request, 'shop/index.html', {'products_object': products})

def cart(request):
    return render(request, 'shop/cart.html')

def login_page(request):
    return render(request, 'shop/login.html')

def search_products(request):
    query = request.GET.get('q')
    if query:
        products = Products.objects.filter(title__icontains=query)
    else:
        products = Products.objects.all()
    return render(request, 'search.html', {'products': products, 'query': query})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to your desired page after login
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'myapp/login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            return redirect('signup')  # redirect to login if you have it
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


