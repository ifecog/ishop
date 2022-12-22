from django.contrib import admin
from .models import Product, Variation
from django.utils.html import format_html

# Register your models here.


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

    def thumbnail(self, object):
        try:
            return format_html('<img src="{}" width="40" style="border-radius: 50px;" />'.format(object.image.url))
        except:
            pass
    thumbnail.short_description = 'photo'

    list_display = ('id', 'thumbnail', 'name', 'category',
                    'price', 'stock', 'is_available')
    list_display_links = ('name', 'thumbnail')
    search_fields = ('name', 'category')


class VariationAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'variation', 'variation_value',
                    'is_active')
    list_display_links = ('product', 'variation', 'variation_value')
    search_fields = ('product', 'variation', 'variation_value')
    list_editable = ('is_active',)


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
