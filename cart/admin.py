from django.contrib import admin
from .models import Cart, CartItem

# Register your models here.


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'quantity')
    list_display_links = ['product']


admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Cart)
