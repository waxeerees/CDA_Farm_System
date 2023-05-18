from django.urls import path
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import  cart_create
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth import views as auth_views

urlpatterns = [
    
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('about-cda', views.about, name='about_cda'),
    path('my-orders', views.customer_orders, name='customer_orders'),
    path('order-view/<int:pk>/', views.customer_order_view, name='customer_order_view'),
 
    path('cart-items/<int:pk>/', views.CartItemView.as_view(), name='cart-details'),
    
    path('cart/', cart_create, name='cart-create'),
  
    path('categories', views.CategoriesView.as_view()),
    path('menu-items', views.menu_items, name='menu_items'),
    path('menu', views.menu_items),
    path('secret/', views.secret),
    path('api-token-auth/', obtain_auth_token),
   # path('signup', views.registerUser),
    path('cart', views.CartItemView.as_view(), name="cart"),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout),
    path('sort-items', views.searchMenu, name="sort-items"),
    path('accounts/login/', auth_views.LoginView.as_view()),
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)