from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import APIView
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework import viewsets
from rest_framework import generics
from rest_framework import serializers
from rest_framework import status
from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import json
from decimal import Decimal
from datetime import datetime, timedelta
import random
from django.utils import timezone
import datetime
from dateutil.relativedelta import relativedelta

from .serializers import OrderSerializer, DeliveryCrewSerializer, MenuItemSerializer
from customer.models import Order, OrderItem, MenuItem
from .models import DeliveryCrew
from django.db.models.functions import ExtractWeekDay

class MenuItemRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MenuItem.objects.filter(pk=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'message': 'Menu item deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        method = request.data.get('method', '').upper()
       
        if method == 'DELETE':
            self.delete(request, *args, **kwargs)
            return redirect('menu_items')
        elif method in ['PUT', 'PATCH']:
            self.partial_update(request, *args, **kwargs)
            return redirect('menu_items')
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return redirect('menu_items')
   
class OrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(pk=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        # perform delete action
        instance = self.get_object()
        instance.delete()
        return redirect('orders')
    
    def put(self, request, *args, **kwargs):
        # perform full update
        return self.update(request, *args, **kwargs)

    # def patch(self, request, *args, **kwargs):
    #     # perform partial update
    #     return self.partial_update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # create order instance
        order = serializer.save()

        # add delivery crew to the order
        delivery_crew_id = request.data.get('delivery_crew')
        delivery_crew = User.objects.get(id=delivery_crew_id)
        order.delivery_crew.add(delivery_crew)

        # set order status to True
        order.status = True
        order.save()

        return redirect('orders')

    def post(self, request, *args, **kwargs):
        method = request.data.get('method', '').upper()

        if method == 'DELETE':
            return self.delete(request, *args, **kwargs)
        elif method in ['PUT', 'PATCH']:
            self.partial_update(request, *args, **kwargs)
            return redirect('orders')
        else:
            return Response({'message': 'Invalid method'}, status=status.HTTP_400_BAD_REQUEST)
         
@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def order_detail(request, pk):
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order does not exist'}, status=404)

    if request.method == 'GET':
        serializer = OrderSerializer(order)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        order.delete()
        return JsonResponse({'message': 'Order deleted successfully'}, status=204)

class OrdersView(LoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):  
    serializer_class = OrderSerializer
    permission_class = [IsAuthenticated]
    
    def get_queryset(selft):
        queryset = Order.objects.all()
        return queryset
    
    def get(self, request, *args, **kwargs):
        orders = self.get_queryset()
        # order_items = OrderItem.objects.select_related('menuitem').all()
        
        page = request.GET.get('page', 1)
        paginator = Paginator(orders, 10)
       
        try:
            orders = paginator.page(page)
        except PageNotAnInteger:
            orders = paginator.page(1)
        except EmptyPage:
            orders = paginator.page(paginator.num_pages)
        return render(request, 'orders.html', {'orders': orders})

    
@api_view(['GET'])
@login_required
def manage_order(request, pk):
    order_details = Order.objects.get(id=pk)
    
    order_items = OrderItem.objects.select_related('menuitem').filter(order_id=pk)
    delivery_crew = DeliveryCrew.objects.all()
    total_price = 0
    
    for item in order_items:
        total_price += item.price
        
    page = request.GET.get('page', 1)
    paginator = Paginator(order_items, 5)
       
    try:
        order_items = paginator.page(page)
    except PageNotAnInteger:
        order_items = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
 
    return render(request, 'manage_order.html', {'order': pk, 'order_items': order_items, 'total_price': total_price, 'crew': delivery_crew, 'order_details':order_details})

def delivery_crew(request):
    crew = DeliveryCrew.objects.all()
    return render(request, 'delivery_crews.html', {'crew': crew})

class DeliveryCrewView(LoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DeliveryCrewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = DeliveryCrew.objects.all()
      
        return queryset

    def get(self, request, *args, **kwargs):
        
        user = request.user
    
        crew = self.get_queryset()
        
       
        page = request.GET.get('page', 1)
        paginator = Paginator(crew, 10)
        try: 
            crew = paginator.page(page)
        except PageNotAnInteger:
            crew = paginator.page(1)
        except EmptyPage:
            cartitems = paginator.page(paginator.num_pages)
        return render(request, "delivery_crews.html", {"crew": crew})
    
    
    def delete(self, request, *args, **kwargs):
        # perform delete action
        instance = self.get_object()
        instance.delete()
        return redirect('cart')

    def put(self, request, *args, **kwargs):
        # perform partial update
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'message': 'Item updated'}, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        # perform partial update
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'message': 'Item updated'}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        method = request.data.get('method', '').upper()

        if method == 'DELETE':
            return self.delete(request, *args, **kwargs)
        elif method in ['PUT', 'PATCH']:
            return self.put(request, *args, **kwargs)
        else:
            return Response({'message': 'Invalid method'}, status=status.HTTP_400_BAD_REQUEST)
    
    def get_object(self):
        queryset = self.get_queryset()
        pk = self.kwargs.get('pk')
        obj = queryset.filter(menuitem_id=pk).first()
        return obj

@login_required
def manager_home(request):
    return render(request, 'manager_dashboard.html')

@csrf_exempt
@login_required
def sales_report(request):
    chart_data = {}
    # Convert data to JSON format for JavaScript
    chart_data_json = json.dumps(chart_data)

    # Context data for the template
    context = {
        'chart_data': chart_data_json,
        'chart_title': 'Products Sold by Day of Week',
    }
    return render(request, 'sales_report.html', context)
  

def get_random_color():
    r = lambda: random.randint(0, 255)
    return ('#%02X%02X%02X' % (r(),r(),r()))

def get_product_sales_doughnut(request):
    # Calculate the start and end dates of this week
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Query the database to get the total sales for each menu item within this week
    data = OrderItem.objects.filter(order__date__range=[start_of_week, end_of_week]).values('menuitem__title').annotate(sales=Sum('price'))

    # Create a list of labels and sales amounts for each menu item
    labels = []
    sales = []
    for item in data:
        labels.append(item['menuitem__title'])
        sales.append(item['sales'])

    # Generate a random color for each menu item
    colors = []
    for i in range(len(labels)):
        colors.append(get_random_color())

    # Create the chart data object
    chart_data = {
        'labels': labels,
        'datasets': [{
            'data': sales,
            'backgroundColor': colors
        }]
    }

    return JsonResponse(chart_data)

def get_product_sales(request):
    # Get the start and end date of the current week
    today = timezone.now().date()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6)

    # Query the database to get the sales data for this week
    data = OrderItem.objects.select_related('order').filter(order__date__gte=start_of_week, order__date__lte=end_of_week, order__status=True).values('order__date', 'menuitem__title').annotate(total_sales=Sum('price'), total_quantity=Sum('quantity'))

    # Create a dictionary to store the sales data for each day of the week
    day_sales = {}
    for i in range(7):
        day = start_of_week + datetime.timedelta(days=i)
        day_sales[day] = {}

    # Fill in the sales data for each day of the week
    for item in data:
        day = item['order__date']
        title = item['menuitem__title']
        total_sales = item['total_sales']
        total_quantity = item['total_quantity']
        if title not in day_sales[day]:
            day_sales[day][title] = {'sales': total_sales, 'quantity': total_quantity}
        else:
            day_sales[day][title]['sales'] += total_sales
            day_sales[day][title]['quantity'] += total_quantity

    # Create the chart data object
    labels = [day.strftime('%A') for day in day_sales.keys()]
    datasets = []
    for title in set([item['menuitem__title'] for item in data]):
        data_sales = [day_sales[day][title]['sales'] if title in day_sales[day] else 0 for day in day_sales.keys()]
        data_quantity = [day_sales[day][title]['quantity'] if title in day_sales[day] else 0 for day in day_sales.keys()]
        datasets.append({
            'label': f"{title} ({sum(data_quantity)}x)",
            'data': data_sales,
            'quantity': data_quantity,
            'backgroundColor': get_random_color()
        })

    chart_data = {
        'labels': labels,
        'datasets': datasets
    }

    return JsonResponse(chart_data)

def get_monthly_product_sales(request):
    # Get the start and end date of the current month
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    end_of_month = start_of_month + relativedelta(months=1, days=-1)

    # Query the database to get the sales data for this month
    data = OrderItem.objects.select_related('order').filter(
        order__date__gte=start_of_month,
        order__date__lte=end_of_month,
        order__status=True
    ).values('order__date', 'menuitem__title').annotate(
        total_sales=Sum('price'),
        total_quantity=Sum('quantity')
    )

    # Create a dictionary to store the sales data for each day of the month
    day_sales = {}
    for i in range(1, end_of_month.day + 1):
        day = start_of_month + datetime.timedelta(days=i-1)
        day_sales[day] = {}

    # Fill in the sales data for each day of the month
    for item in data:
        day = item['order__date']
        title = item['menuitem__title']
        total_sales = item['total_sales']
        total_quantity = item['total_quantity']
        if title not in day_sales[day]:
            day_sales[day][title] = {'sales': total_sales, 'quantity': total_quantity}
        else:
            day_sales[day][title]['sales'] += total_sales
            day_sales[day][title]['quantity'] += total_quantity

    # Create the chart data object
    labels = [day.strftime('%d/%m') for day in day_sales.keys()]
    datasets = []
    for title in set([item['menuitem__title'] for item in data]):
        data_sales = [day_sales[day][title]['sales'] if title in day_sales[day] else 0 for day in day_sales.keys()]
        data_quantity = [day_sales[day][title]['quantity'] if title in day_sales[day] else 0 for day in day_sales.keys()]
        datasets.append({
            'label': f"{title} ({sum(data_quantity)}x)",
            'data': data_sales,
            'quantity': data_quantity,
            'backgroundColor': get_random_color()
        })

    chart_data = {
        'labels': labels,
        'datasets': datasets
    }

    return JsonResponse(chart_data)

def monthly_sales_report(request):
    return render(request, 'monthly_sales_report.html')

def get_monthly_sales(request, year=None, month=None):
    if not year or not month:
        # Use the current year and month if not provided
        today = timezone.now().date()
        year = today.year
        month = today.month

    # Get the start and end date of the month
    start_of_month = datetime.date(year, month, 1)
    end_of_month = start_of_month + relativedelta(months=1, days=-1)

    # Query the database to get the sales data for this month
    data = OrderItem.objects.select_related('order').filter(
        order__date__gte=start_of_month, order__date__lte=end_of_month, 
        order__status=True
    ).values('order__date', 'menuitem__title').annotate(
        total_sales=Sum('price'), total_quantity=Sum('quantity')
    )

    # Create a dictionary to store the sales data for each day of the month
    day_sales = {}
    for i in range((end_of_month - start_of_month).days + 1):
        day = start_of_month + datetime.timedelta(days=i)
        day_sales[day] = {}

    # Fill in the sales data for each day of the month
    for item in data:
        day = item['order__date']
        title = item['menuitem__title']
        total_sales = item['total_sales']
        total_quantity = item['total_quantity']
        if title not in day_sales[day]:
            day_sales[day][title] = {'sales': total_sales, 'quantity': total_quantity}
        else:
            day_sales[day][title]['sales'] += total_sales
            day_sales[day][title]['quantity'] += total_quantity

    # Create the chart data object
    labels = [day.strftime('%-e %b') for day in day_sales.keys()]
    datasets = []
    for title in set([item['menuitem__title'] for item in data]):
        data_sales = [day_sales[day][title]['sales'] if title in day_sales[day] else 0 for day in day_sales.keys()]
        data_quantity = [day_sales[day][title]['quantity'] if title in day_sales[day] else 0 for day in day_sales.keys()]
        datasets.append({
            'label': f"{title} ({sum(data_quantity)}x)",
            'data': data_sales,
            'quantity': data_quantity,
            'backgroundColor': get_random_color()
        })

    chart_data = {
        'labels': labels,
        'datasets': datasets
    }

    return JsonResponse(chart_data)


def get_random_color():
    return '#' + ''.join(random.choice('0123456789ABCDEF') for i in range(6))