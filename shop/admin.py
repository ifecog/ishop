from django.contrib import admin
from .models import Category
from django.utils.html import format_html

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

    def thumbnail(self, object):
        return format_html('<img src="{}" width="40" style="border-radius: 50px;" />'.format(object.image.url))

    thumbnail.short_description = 'photo'

    list_display = ('id', 'thumbnail', 'name')
    list_display_links = ('name', 'thumbnail')
    search_fields = ['name']


admin.site.register(Category, CategoryAdmin)
