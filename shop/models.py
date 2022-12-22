from django.db import models
from ckeditor.fields import RichTextField
from django.urls import reverse

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = RichTextField()
    image = models.ImageField(upload_to='media/photos/%y/%m/%d/', blank=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_url(self):
        return reverse('products_by_category', args=[self.slug])
