from rest_framework import serializers
from userApp.models import Product
from userApp.models import ProductCategory
from .models import MenuItem, Category, Cart, Order, OrderItem

class OrderSerializer(serializers.ModelSerializer):
  
    class Meta:
        model = Order
        fields = '__all__'
        
class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = '__all__'

class ProductItemSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    class Meta:
        model = Product
        fields = ['name', 'quantity', 'price', 'image', 'category']
 

class CategorySerializer (serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','title']

class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)
    class Meta:
        model = MenuItem
        fields = ['id','title','price','inventory','category','category_id']

class CartItemSerializer(serializers.ModelSerializer):
    menuitem_image = serializers.ImageField(source='MenuItem.image')
    
    class Meta:
        model = Cart
        fields = '__all__'
        
class CreditCardSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    card_number = serializers.CharField()
    expiration_date = serializers.CharField(max_length=5)

    def validate_expiration_date(self, value):
        """
        Validate the expiration_date field, which should be in the format MM/YY.
        """
        parts = value.split('/')
        if len(parts) != 2:
            raise serializers.ValidationError('Expiration date should be in the format MM/YY.')

        try:
            month = int(parts[0])
            year = int(parts[1])
        except ValueError:
            raise serializers.ValidationError('Invalid expiration date.')

        if month < 1 or month > 12:
            raise serializers.ValidationError('Month should be between 1 and 12.')

        if year < 0 or year > 99:
            raise serializers.ValidationError('Year should be between 00 and 99.')

        # add 2000 to the year, since it is a two-digit representation of the year
        year += 2000

        # return the formatted expiration date string
        return f'{month:02d}/{year:02d}'

    def validate(self, data):
        """
        Validate the credit card information.
        """
        card = CreditCard.objects.filter(
            full_name__iexact=data['first_name'] + ' ' + data['last_name'],
            card_number=data['card_number'],
            expiration_date=data['expiration_date']
        ).first()

        if not card:
            raise serializers.ValidationError('Invalid credit card information.')

        # check if there is enough money in the account to make the payment
        if card.account_balance < order_total:
            raise serializers.ValidationError('Not enough funds to complete the payment.')

        # update the account balance and save the credit card
        card.account_balance -= order_total
        card.save()

        return data
