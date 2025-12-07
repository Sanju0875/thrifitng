from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from product.views import login_view
from .views import signup_view

urlpatterns = [
    path('', views.home, name='home'),

    # Products
    path('products/', views.products_view, name='products'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    # path('search/', views.search_products, name='search_products'),

    # Authentication
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    # Cart & Checkout
    path('cart/', views.cart, name='cart'),  # Updated to use DB-backed cart
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:pk>/', views.update_cart, name='update_cart'),
    path('cart/increase/<int:pk>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:pk>/', views.decrease_quantity, name='decrease_quantity'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),

    # Checkout & Orders
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/<int:order_id>/', views.payment_view, name='payment'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
