from django.contrib import admin

from .models import Cart

class CartAdmin( admin.ModelAdmin ):
  list_display = ( 'user', 'food_item', 'quantity', 'updated_at' )

# Register your models here.
admin.site.register( Cart, CartAdmin )