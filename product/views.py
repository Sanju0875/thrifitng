from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Product, CartItem, Order, OrderItem, CustomerInterested, Transaction
from .forms import SignupForm, LoginForm, OrderForm
from .utils import get_recommendations_ml_from_transactions
import uuid

def home(request):
    total_quantity = 0
    if request.user.is_authenticated:
        total_quantity = CartItem.objects.filter(user=request.user).count()

    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(title__icontains=query)
    else:
        products = Product.objects.all()
        new_arrivals = Product.objects.order_by('-id')[:6]

    return render(request, 'shop/home.html', {
        'products_object': products,
        'new_arrivals': new_arrivals if not query else [],
        'total_quantity': total_quantity,
        'query': query
    })


# def products_view(request):
#     total_quantity = 0
#     if request.user.is_authenticated:
#         total_quantity = CartItem.objects.filter(user=request.user).count()

#     query = request.GET.get('q')
#     if query:
#         products = Product.objects.filter(title__icontains=query)
#     else:
#         products = Product.objects.all()

#     # Get recommendations only for logged-in users
#     recommended_products = []
#     if request.user.is_authenticated:
#         last_viewed = CustomerInterested.objects.filter(user=request.user).order_by('-viewed_at')[:5]
#         last_viewed_products = [item.product for item in last_viewed]
#         if last_viewed_products:
#             recommended_products = get_recommendations(last_viewed_products, top_n=5)

#     return render(request, 'shop/products.html', {
#         'products_object': products,
#         'recommended_products': recommended_products,
#         'total_quantity': total_quantity
#     })

def products_view(request):
    total_quantity = 0
    if request.user.is_authenticated:
        total_quantity = CartItem.objects.filter(user=request.user).count()

    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(title__icontains=query)
    else:
        products = Product.objects.all()

    # ML-based recommendations for logged-in users
    recommended_products = []
    if request.user.is_authenticated:
        # Get all orders of the user with successful transactions
        successful_orders = Transaction.objects.filter(
            order__user=request.user, 
        ).values_list('order', flat=True)

        # Get all products in these successful orders
        purchased_items = OrderItem.objects.filter(
            order_id__in=successful_orders
        ).select_related('product')

        if purchased_items.exists():
            recommended_products = get_recommendations_ml_from_transactions(purchased_items, top_n=5)

    return render(request, 'shop/products.html', {
        'products_object': products,
        'recommended_products': recommended_products,
        'total_quantity': total_quantity
    })


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect(reverse("home"))
        else:
            return render(request, 'shop/signup.html', {'form': form})

    form = SignupForm()
    return render(request, 'shop/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'shop/login.html', {'form': form})
    else:
        form = LoginForm()
    return render(request, 'shop/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product, price=product.price)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    messages.success(request, f"{product.title} added to your cart!")
    return redirect('cart')


@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.subtotal for item in cart_items)
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total_price': total_price})


@login_required
def update_cart(request, pk):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart_item = get_object_or_404(CartItem, user=request.user, product_id=pk)
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('cart')


@login_required
def increase_quantity(request, pk):
    cart_item = get_object_or_404(CartItem, user=request.user, product_id=pk)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart')


@login_required
def decrease_quantity(request, pk):
    cart_item = get_object_or_404(CartItem, user=request.user, product_id=pk)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')


@login_required
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(CartItem, user=request.user, product_id=pk)
    cart_item.delete()
    return redirect('cart')


@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.subtotal for item in cart_items)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        print(request.POST)
        if form.is_valid():
            # Create order with pending status
            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                status='pending'
            )
            # Save billing info
            billing_info = form.save(commit=False)
            billing_info.order = order
            billing_info.save()

            # Save order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                )

            # Clear cart
            cart_items.delete()

            return redirect('payment', order_id=order.id)
        else:
            print(form.errors)
            form = OrderForm(request.POST)
    else:
        form = OrderForm()

    return render(request, 'shop/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price
    })


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.user.is_authenticated:
        CustomerInterested.objects.get_or_create(user=request.user, product=product)
    return render(request, 'shop/product_detail.html', {'product': product})

@login_required
def payment_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status == 'paid':
        return redirect('order_detail', order_id=order.id)

    if request.method == 'POST':
        # Simulate payment success
        transaction = Transaction.objects.create(
            order=order,
            transaction_id=str(uuid.uuid4()),
            amount=order.total_price,
            status='success'
        )
        order.status = 'paid'
        order.save()
        return redirect('order_detail', order_id=order.id)

    return render(request, 'shop/payment.html', {
        'order': order
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    billing_info = getattr(order, 'billing_info', None)  # OneToOneField
    order_items = order.items.all()  # Related name from OrderItem
    transactions = order.transactions.all()  # Related name from Transaction

    return render(request, 'shop/order_detail.html', {
        'order': order,
        'billing_info': billing_info,
        'order_items': order_items,
        'transactions': transactions,
    })
