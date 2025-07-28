from .import views
from django.urls import path
from product.views import login_view
from .views import signup_view
urlpatterns = [
    
path('index/', views.index, name='index'),  
path('', views.home, name='home'),
path('cart/', views.cart, name='cart'),          # Cart page
path('login/', views.login_page, name='login'),
path('search/', views.search_products, name='search_products'),
path('signup/', views.signup_view, name='signup'),
]
