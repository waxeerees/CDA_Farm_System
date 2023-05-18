from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse

from rest_framework import generics
from rest_framework.mixins import CreateModelMixin
from .serializers import UserCreateSerializer
from django.contrib.auth.models import User

from django.http import HttpResponse, HttpRequest
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from customer.models import MenuItem
from django.contrib.auth.models import Group

from django.shortcuts import render
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncDate

from customer.models import Order, OrderItem

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
           
            if request.user.is_superuser:
                return redirect(reverse('admin:index'))
            else :
                # Check if the user belongs to a particular group
                if user.groups.filter(name='Customers').exists():
                    return redirect('home')
                    # User belongs to 'mygroup'
                    # Do something here
                elif user.groups.filter(name="Managers").exists():
                    return redirect('manager_dashboard')
                else:
                    return redirect("home")
            
                
        else:
            # Return an 'invalid login' error message.
            messages.success(request, ("There is an error. Try again... "))
            return redirect('home')
    else:
        return redirect('home')
    

def logout_view(request):
    logout(request)
    messages.success(request, ("You were logged out!"))
    return redirect('home')

@api_view(['GET'])
def home(request):
    
    if  request.user.is_authenticated:
        if request.user.groups.filter(name="Managers").exists():
            return redirect('manager_dashboard')
       
        if request.user.groups.filter(name='Customers').exists():
            menu_items = MenuItem.objects.select_related('category').all()
            return render(request, 'index.html', {'products': menu_items})
        
        if request.user.is_superuser:
            return redirect(reverser('admin:index'))
    else: 
        menu_items = MenuItem.objects.select_related('category').all()
        return render(request, 'index.html', {'products': menu_items})

def manager_dashboard(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login requred!")
        return redirect('home')
    else:
        if  request.user.groups.filter(name="Managers").exists():
            order_items = Order.objects.all()
        
            today = timezone.now().date()
            start_date = today - timedelta(days=7)
            data = []
            # Fetch the order data for the date range
            orders = Order.objects.filter(date__gte=start_date, date__lte=today, status=True)

            # Calculate the total revenue and number of orders per day
            daily_totals = orders.annotate(order_date=TruncDate('date')).values('order_date').annotate(total=Sum('total'), count=Count('id'))

            # Fetch the order item data for the date range
            items = OrderItem.objects.filter(order__date__gte=start_date, order__date__lte=today)

            # Calculate the top selling menu items for the date range
            top_items = items.values('menuitem__title').annotate(total=Sum('quantity')).order_by('-total')[:10]

            # context = {
            #     'daily_totals': daily_totals,
            #     'top_items': top_items,
            # }

            for item in order_items:
                new_item = item.total
                data.append(new_item)
                print(new_item)
                
            

            my_list = [float(x) for x in data]
        
            
            return render(request, 'manager_dashboard.html', {'chart_data': my_list})
            #return render(request, 'manager_dashboard.html')
        else:
            messages.info(request, "Access denied")
            return redirect('home')

@api_view(['POST'])
def create_user(request):
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        group, created = Group.objects.get_or_create(name='Customers')
        group.user_set.add(user)
        messages.info(request, "Account created")
        return redirect('home')
    else:
        error_messages = []
        for field_errors in serializer.errors.values():
            for error in field_errors:
                error_messages.append(error)
        error_message = "\n".join(error_messages)
        
        messages.warning(request, error_message)
        return redirect('home')