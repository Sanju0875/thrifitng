from .import views
from django.urls import path
from product.views import login_view
from django.contrib.auth import views as auth_views
from .views import signup_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
path('index/', views.index, name='index'),  
path('', views.home, name='home'),         
path('login/', login_view, name='login'),
path('search/', views.search_products, name='search_products'),
path('product/<int:pk>/', views.product_detail, name='product_detail'),
path('checkout/', views.checkout_view, name='checkout'),
 path('order-summary/', views.order_summary, name='order_summary'),

    
    # All cart routes use <int:pk>
path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
path('update-cart/<int:pk>/', views.update_cart, name='update_cart'),
path('cart/increase/<int:pk>/', views.increase_quantity, name='increase_quantity'),
path('cart/decrease/<int:pk>/', views.decrease_quantity, name='decrease_quantity'),
path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
path('signup/', views.signup_view, name='signup'), 
path('cart/', views.cart_view, name='cart'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
