from django.contrib import admin

from .models import Cart, Tax

class CartAdmin( admin.ModelAdmin ):
  list_display = ( 'user', 'food_item', 'quantity', 'updated_at' )

class TaxAdmin( admin.ModelAdmin ):
  list_display = ( 'tax_type', 'tax_rate', 'is_active' )

# Register your models here.
admin.site.register( Cart, CartAdmin )
admin.site.register( Tax, TaxAdmin )