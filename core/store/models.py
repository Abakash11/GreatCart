from django.db import models
from category.models import Category
from django.urls import reverse
from my_accounts.models import Accounts
from django.db.models import Avg
# Create your models here.
class Product(models.Model):
    product_name=models.CharField(max_length=200,unique=True)
    slug=models.SlugField(max_length=200,unique=True)
    descriptions=models.TextField(max_length=500,blank=True)
    price=models.IntegerField()
    image=models.ImageField(upload_to='photos/product')
    stock=models.IntegerField()
    is_available=models.BooleanField(default=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    create_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)
    colors = models.CharField(max_length=100, blank=True)
    sizes = models.CharField(max_length=100, blank=True)
    def avg_rating(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(rating__avg=Avg('rating'))
        avg_rating = 0
        if reviews['rating__avg'] != None:
            avg_rating = float(reviews['rating__avg'])
        return avg_rating

    def get_url(self):
        return reverse('product_detail',args=[self.category.slug,self.slug])
    def __str__(self):
        return self.product_name
    
class ReviewRating(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    user=models.ForeignKey(Accounts,on_delete=models.CASCADE)
    subject=models.CharField(max_length=100,blank=True)
    review=models.TextField(max_length=500,blank=True)
    rating=models.FloatField()
    ip=models.CharField(max_length=20,blank=True)
    status=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
    
class ProductGallery(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    image=models.ImageField(upload_to='photos/product_gallery')
    
    class Meta:
        verbose_name_plural='Product Gallery'

    def __str__(self):
        return self.product.product_name