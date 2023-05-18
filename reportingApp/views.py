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

from commerce.serializers import OrderSerializer, DeliveryCrewSerializer, MenuItemSerializer
from customer.models import Order, OrderItem, MenuItem
from commerce.models import DeliveryCrew
from django.db.models.functions import ExtractWeekDay
# Create your views here.  

def get_random_color():
    r = lambda: random.randint(0, 255)
    return ('#%02X%02X%02X' % (r(),r(),r()))

def get_weekly_sales(request):
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
        data_sales = [float(day_sales[day][title]['sales']) if title in day_sales[day] else 0 for day in day_sales.keys()]
        data_quantity = [float(day_sales[day][title]['quantity']) if title in day_sales[day] else 0 for day in day_sales.keys()]

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
    
     # Convert data to JSON format for JavaScript
    chart_data_json = json.dumps(chart_data)

    # Context data for the template
    context = {
        'chart_data': chart_data_json,
        'chart_title': 'Products sold by day of week',
    }

    return render(request, 'sales_report.html', context)


def get_monthly_sales(request):
    # Get the start and end date of the month requested by the user
    month = int(request.GET.get('month', timezone.now().month))
    year = int(request.GET.get('year', timezone.now().year))
    start_of_month = datetime.date(year, month, 1)
    end_of_month = start_of_month + relativedelta(day=31)

    # Query the database to get the sales data for this month
    data = OrderItem.objects.select_related('order').filter(
        order__date__gte=start_of_month,
        order__date__lte=end_of_month,
        order__status=True
    ).values('order__date', 'menuitem__title').annotate(
        total_sales=Sum('price'), total_quantity=Sum('quantity')
    )

    # Create a dictionary to store the sales data for each day of the month
    day_sales = {}
    for i in range(31):
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
    labels = [day.strftime('%d') for day in day_sales.keys()]
    datasets = []
    for title in set([item['menuitem__title'] for item in data]):
        data_sales = [float(day_sales[day][title]['sales']) if title in day_sales[day] else 0 for day in day_sales.keys()]
        data_quantity = [float(day_sales[day][title]['quantity']) if title in day_sales[day] else 0 for day in day_sales.keys()]

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
    
     # Convert data to JSON format for JavaScript
    chart_data_json = json.dumps(chart_data)

    # Context data for the template
    context = {
        'chart_data': chart_data_json,
        'chart_title': f"Products sold in {start_of_month.strftime('%B %Y')}",
        'selected_month': month,
        'selected_year': year,
    }

    return render(request, 'monthly_sales_report.html', context)

def sortable_monthly_sales(request):
    # Get the start and end date of the month requested by the user
    month = int(request.GET.get('month', timezone.now().month))
    year = int(request.GET.get('year', timezone.now().year))
    start_of_month = datetime.date(year, month, 1)
    end_of_month = start_of_month + relativedelta(day=31)

    # Query the database to get the sales data for this month
    data = OrderItem.objects.select_related('order').filter(
        order__date__gte=start_of_month,
        order__date__lte=end_of_month,
        order__status=True
    ).values('order__date', 'menuitem__title').annotate(
        total_sales=Sum('price'), total_quantity=Sum('quantity')
    )

    # Create a dictionary to store the sales data for each day of the month
    day_sales = {}
    for i in range(31):
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
    labels = [day.strftime('%d') for day in day_sales.keys()]
    datasets = []
    for title in set([item['menuitem__title'] for item in data]):
        data_sales = [float(day_sales[day][title]['sales']) if title in day_sales[day] else 0 for day in day_sales.keys()]
        data_quantity = [float(day_sales[day][title]['quantity']) if title in day_sales[day] else 0 for day in day_sales.keys()]

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
    
    # Convert data to JSON format for JavaScript
    chart_data_json = json.dumps(chart_data)

    # Context data for the template
    context = {
        'chart_data': chart_data_json,
        'chart_title': f"Products sold in {start_of_month.strftime('%B %Y')}",
        'selected_month': month,
        'selected_year': year,
    }

    return render(request, 'sortable_monthly_report.html', context)
