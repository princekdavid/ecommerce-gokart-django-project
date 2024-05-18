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
    
variation_category_choice = (
    ('color', 'color'),
    ('size' , 'size'),
)

# Create Variation Manager to change variation 
class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category = 'color', is_active =True)
    
    def sizes(self):
        return super(VariationManager, self).filter(variation_category = 'size', is_active =True)


class Variation(models.Model):
    product      = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=50, choices= variation_category_choice)
    variation_value = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    # call VariationManager
    object = VariationManager()

    def __str__(self):
        return self.variation_value
