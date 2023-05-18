from django.contrib import admin
from customer.models import Order
from customer.models import OrderItem
from .models import DeliveryCrew

# Register your models here.
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(DeliveryCrew)