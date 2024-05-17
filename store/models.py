from django.db import models
from category.models import Category
from django.urls import reverse

# Create your models here.
class Product(models.Model):
    product_name      = models.CharField(max_length=200, unique=True)
    slug              = models.SlugField(max_length=200, unique=True)
    product_description = models.TextField(max_length=500, blank=True)
    product_price      = models.IntegerField()
    product_image      = models.ImageField(upload_to='photos/products', height_field=None, width_field=None, max_length=None)
    stock              = models.IntegerField()
    is_available       = models.BooleanField()
    category           = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date       = models.DateTimeField(auto_now_add=True)
    modified_date      = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_details', args=[self.category.slug, self.slug])


    def __str__(self):
        return self.product_name
    