from django.db import models
from django.contrib.auth.models import User
from commerce.models import DeliveryCrew

# Create your models here.
class Category(models.Model):
    #slug = models.SlugField()
    title = models.CharField(max_length=255)

    def __str__(self)-> str:
        return self.title
    

class MenuItem(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    inventory = models.SmallIntegerField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, default=1)
    image = models.ImageField(upload_to='images/', blank=True)

    def formatted_price(self):
        return '{:,.2f}'.format(self.price)
    
    def __str__(self)-> str:
        return self.title

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=20, decimal_places=2)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    
    class Meta:
        unique_together = ('menuitem', 'user')
   
        
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=255, null=True)
    lastname = models.CharField(max_length=255, null=True)
    delivery_address = models.CharField(max_length=1000, null=True)
    phone_number = models.IntegerField(max_length=11, null=True)
    delivery_crew = models.ForeignKey('commerce.DeliveryCrew', on_delete=models.SET_NULL, related_name="delivery_crew", null=True)
    status = models.BooleanField(db_index=True, default=0)
    total = models.DecimalField(max_digits=20, decimal_places=0)
    date = models.DateField(db_index=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=20, decimal_places=0)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    class Meta:
        unique_together = ('order', 'menuitem')
    
class ExpirationDateField(models.CharField):
    max_length = 5

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return value.strftime('%m/%y')

    def to_python(self, value):
        if isinstance(value, str):
            return value
        if value is None:
            return value
        return datetime.date(year=int(value[3:]), month=int(value[:2]), day=1)

    def get_prep_value(self, value):
        if isinstance(value, str):
            return value
        if value is None:
            return value
        return value.strftime('%m/%y')


class CreditCard(models.Model):
    full_name = models.CharField(max_length=50)
    card_number = models.CharField(max_length=16)
    expiration_date = models.DateField()
    cvv = models.CharField(max_length=3)
    account_balance = models.DecimalField(max_digits=20, decimal_places=2)

    def save(self, *args, **kwargs):
     # Check if expiration_date is a string
        if isinstance(self.expiration_date, str):
            # Parse the expiration_date string to a date object before saving
            month, year = self.expiration_date.split('/')
            year = int(year) + 2000  # convert YY to YYYY format
            self.expiration_date = date(year, int(month), 1)
        super(CreditCard, self).save(*args, **kwargs)

