from rest_framework import serializers
from customer.models import Order, OrderItem, MenuItem
from .models import DeliveryCrew

class OrderSerializer(serializers.ModelSerializer):
  
    class Meta:
        model = Order
        fields = '__all__'
        
class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = '__all__'

class DeliveryCrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryCrew
        fields = '__all__'
        
class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'