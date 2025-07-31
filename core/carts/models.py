from django.db import models
from store.models import Product
from my_accounts.models import Accounts


# Create your models here.
class Cart(models.Model):
    cart_id = models.CharField(max_length=50)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart_id
    
class CartItem(models.Model):
    user=models.ForeignKey(Accounts,on_delete=models.CASCADE,null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    colour=models.CharField(max_length=50,blank=True)
    size=models.CharField(max_length=50,blank=True)
    
    def total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return str(self.product)