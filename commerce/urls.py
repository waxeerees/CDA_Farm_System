from django.urls import path
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('manage-dashboard', views.manager_home, name='manager_dashboard'),
    path('orders', views.OrdersView.as_view(), name='orders'),
    path('order-detail/<int:pk>/', views.OrderRetrieveUpdateDestroyAPIView.as_view(), name='order_detail'),
    path('manage-order/<int:pk>/', views.manage_order, name='order_management'),
   
    path('delivery-crews/', views.delivery_crew, name='delivery_crews'),
    path('delivery-crew/<int:pk>', views.DeliveryCrewView.as_view(), name='crew_details'),
    path('add-product', views.MenuItemRetrieveUpdateDestroyAPIView.as_view(), name='add_item'),
    path('manage-product/<int:pk>', views.MenuItemRetrieveUpdateDestroyAPIView.as_view(), name='manage_item'),
    path('get-product-sales-bar/', views.get_product_sales, name='get_product_sales_bar'),
    path('get-product-sales-doughnut/', views.get_product_sales, name='get_product_sales_doughnut'),
    path('sales/<int:year>/<int:month>/', views.get_monthly_sales, name='monthly_sales'),
    path('sales/', views.get_monthly_sales, name='current_month_sales'),

]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)