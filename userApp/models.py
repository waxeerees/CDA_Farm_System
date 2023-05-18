from django.db import models


# Create your models here.
class ProductCategory(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=200, default="")

    def __str__(self) -> str:
        return self.title
    
    
class Product(models.Model):
    name = models.CharField(max_length=100, default="")
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='images/', blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, default=1)
    

    def __str__(self) -> str:
        return self.name    



    
