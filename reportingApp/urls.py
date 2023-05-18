from django.urls import path
from django.conf import settings
from django.http import HttpResponse
from django.conf.urls.static import static
from . import views
urlpatterns = [
    path('weekly-sales', views.get_weekly_sales, name='weekly_sales_report'),
    path('sortable-monthly-sales/', views.sortable_monthly_sales, name='sortable_monthly_sales'),
    path('sales/', views.get_monthly_sales, name='current_month_sales'),
]
