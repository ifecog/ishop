from django.db import models
from ckeditor.fields import RichTextField
from shop.models import Category
from datetime import datetime
from django.urls import reverse

# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = RichTextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='media/photos/%y/%m/%d/', blank=True)
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    slug = models.SlugField(max_length=100, unique=True)
    created_date = models.DateTimeField(blank=True, default=datetime.now)
    modified_date = models.DateTimeField(blank=True, default=datetime.now)

    def __str__(self):
        return self.name

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

class VariationManager(models.Manager):
    def color(self):
        return super(VariationManager, self).filter(variation='color', is_active=True)

    def size(self):
        return super(VariationManager, self).filter(variation='size', is_active=True)

class Variation(models.Model):
    variation_choice = (
        ('color', 'color'),
        ('size', 'size')
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation = models.CharField(max_length=45, choices=variation_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(blank=True, default=datetime.now)
    
    objects = VariationManager()

    def __str__(self):
        return self.variation_value
    