from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib import messages
from rest_framework.permissions import AllowAny
from django.core.paginator import Paginator, EmptyPage
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework import status
from rest_framework import generics
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.db.models import Q
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from decimal import Decimal
from django.utils import timezone
from django.db import transaction

#from .models import Product
from userApp.models import Product
from userApp.models import ProductCategory
from .serializers import ProductItemSerializer
from .models import MenuItem, Category, Cart, Order, OrderItem, CreditCard, DeliveryCrew
from .serializers import MenuItemSerializer, CategorySerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer


# Create your views here.
@api_view(['GET'])
def home(request):
    menu_items = MenuItem.objects.select_related('category').all()
    
    return render(request, 'index.html', {'products': menu_items})

def about(request):    
    return render(request, 'about.html')


class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price', 'inventory']
    filterset_fields = ['price', 'inventory']
    search_fields = ['title']

#Working with pagination in views 
def menu_items(request):
    categories = Category.objects.all()
    menu_items = MenuItem.objects.all()
    page = request.GET.get('page', 1)

    paginator = Paginator(menu_items, 7)
    try:
        menu_items = paginator.page(page)
    except PageNotAnInteger:
        menu_items = paginator.page(1)
    except EmptyPage:
        menu_items = paginator.page(paginator.num_pages)
    context = {
        'items':menu_items, 'categories':categories
    }
    return render(request, 'products.html', context)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def secret(request):
    return Response({'Message':'Some secret message'})

class ProductsView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductItemSerializer

class ProductItemsView(generics.ListAPIView, generics.CreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = ProductItemSerializer


class SingleProductItemView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = ProductItemSerializer

class SearchResultsView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductItemSerializer
   # permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        query = self.request.GET.get("q")
        object_list = Product.objects.select_related('category').filter(
            Q(name__icontains=query)  | Q(category__title__icontains=query)
        )
        return render(self.request, 'partials/_menu-items.html', {'products':object_list})

def searchMenu(request):
    query = request.GET.get("q")
    object_list = MenuItem.objects.select_related('category').filter(
        Q(title__icontains=query)  | Q(category__title__icontains=query)
    )
    
    return render(request, 'index.html', {'products':object_list})


class CartItemView(LoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Cart.objects.filter(user=self.request.user)
        queryset = queryset.select_related('menuitem')
        return queryset

    def get(self, request, *args, **kwargs):
        
        user = request.user
    
        cartitems = self.get_queryset()
        
        total_price = 0
        
        for element in cartitems:
            total_price += element.price
          
        
        page = request.GET.get('page', 1)
        paginator = Paginator(cartitems, 10)
        try: 
            cartitems = paginator.page(page)
        except PageNotAnInteger:
            cartitems = paginator.page(1)
        except EmptyPage:
            cartitems = paginator.page(paginator.num_pages)
        return render(request, "cart.html", {"cartitems": cartitems, "total_price": total_price})
    
    
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
    
       
@api_view(['GET', 'PUT', 'DELETE'])
def cart_detail(request, pk):
    if not request.user.is_autnticated:
        messages.error(request, "Login required!")
        return redirect('home')
    else:    
        form_data = request.data
        
        try:
            item = Cart.objects.get(menuitem_id=pk, user=request.user)
        except Cart.DoesNotExist:
            return Response({"form":form_data}, status=status.HTTP_404_NOT_FOUND)
        
        if request.method == 'GET':
            serializer = CartItemSerializer(item)
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            serializer = CartItemSerializer(item, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def cart_create(request):
    if not request.user.is_authenticated:
        messages.error(request, "Login required!")
        return redirect('home')
    else:
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        messages.success(request, "Login required!")
        return redirect('home')
    else:    
        menuitem = MenuItem.objects.select_related('category').get(id=product_id)
        quantity = request.POST['quantity']
        price = Decimal(Decimal(quantity) * menuitem.price)
        cart = Cart(user=request.user, menuitem=menuitem, unit_price=menuitem.price, price=price, quantity=quantity)
        cart.save()
        return redirect('home')

@transaction.atomic
def checkout(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        order_total = 0
        
        print(request.POST.get('firstName'))
        # Calculate order total
        for item in cart_items:
            order_total += item.quantity * item.price

        # Validate credit card and account balance
        try:
            credit_card = CreditCard.objects.get(full_name=request.POST.get('full_name'),
                                                 card_number=request.POST.get('card_number'), 
                                                 expiration_date=request.POST.get('expiration_date'),
                                                 cvv=request.POST.get('cvv'))

            if credit_card.account_balance < order_total:
                messages.error(request, "Not enough funds in the account")
                return redirect('cart')
        except CreditCard.DoesNotExist:
            messages.error(request, "Invalid credit card details")
            return redirect('cart')

        # Create the order and order items
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                firstname = request.POST.get('firstName'),
                lastname = request.POST.get('lastName'),
                total=order_total,
                date=timezone.now()
            )

            for item in cart_items:
                menuitem = item.menuitem
                quantity = item.quantity

                # Reduce the inventory of the menuitem
                if menuitem.inventory < quantity:
                    # Not enough inventory
                    messages.error(request, f"Not enough inventory for {menuitem.title}")
                    return redirect('cart')
                else:
                    menuitem.inventory -= quantity
                    menuitem.save()

                OrderItem.objects.create(
                    order=order,
                    menuitem=menuitem,
                    quantity=quantity,
                    unit_price=item.unit_price,
                    price=item.price
                )

            # Deduct the amount from the user's account balance
            credit_card.account_balance -= order_total
            credit_card.save()

        # Clear the cart
        Cart.objects.filter(user=request.user).delete()

        # Redirect to the home page
        messages.success(request, "Order placed successfully")
        return redirect('home')
    else:
        messages.error(request, "Login required")
        return redirect('home')
    
@api_view(['GET'])
@login_required
def customer_order_view(request, pk):
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
 
    return render(request, 'customer_order_view.html', {'order': pk, 'order_items': order_items, 'total_price': total_price, 'crew': delivery_crew, 'order_details':order_details})
    

def customer_orders(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login requred!")
        return redirect('home')
    else:
        orders = Order.objects.filter(user=request.user)
            
        page = request.GET.get('page', 1)
        paginator = Paginator(orders, 10)
        
        try:
            orders = paginator.page(page)
        except PageNotAnInteger:
            orders = paginator.page(1)
        except EmptyPage:
            orders = paginator.page(paginator.num_pages)
        return render(request, 'customer_order.html', {'orders': orders})