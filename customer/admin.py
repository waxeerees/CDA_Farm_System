from django.contrib import admin
from userApp.models import Product
from userApp.models import ProductCategory
from .models import MenuItem
from .models import Category
from .models import CreditCard


# Register your models here.
admin.site.register(MenuItem)
admin.site.register(Category)
admin.site.register(CreditCard)

