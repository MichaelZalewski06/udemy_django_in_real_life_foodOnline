from django.contrib import admin

from .models import Order, OrderedFood, Payment

class OderedFoodInline( admin.TabularInline ):
  model = OrderedFood
  readonly_fields = [ 'order', 'payment', 'user', 'fooditem', 'quantity', 'price', 'amount' ]
  extra = 0

class OdersAdmin( admin.ModelAdmin ):
  list_display = [ 'order_number', 'name', 'phone', 'mail', 'total', 'payment_method', 
        'status', 'order_placed_to', 'is_ordered' ]
  inlines = [OderedFoodInline]

# Register your models here.
admin.site.register( Order )
admin.site.register( OrderedFood )
admin.site.register( Payment )

