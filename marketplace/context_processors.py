from .models import Cart, Tax
from menu.models import FoodItem

def get_cart_count( request ):
  cart_count = 0
  if request.user.is_authenticated:
    try:
      cart_items = Cart.objects.filter( user=request.user )
      for cart_item in cart_items:
        cart_count += cart_item.quantity
    except:
      cart_count = 0
  return dict( cart_count=cart_count )

def get_cart_totals( request ):
  subtotal = 0
  grand_total = 0
  if request.user.is_authenticated:
    cart_items = Cart.objects.filter( user=request.user )
    for item in cart_items:
      food_item = FoodItem.objects.get( pk=item.food_item.id )
      subtotal += ( food_item.price * item.quantity )

  tax_list = []
  tax_total = 0
  taxes = Tax.objects.filter( is_active=True )
  for tx in taxes:
    tax_type = tx.tax_type
    tax_rate = tx.tax_rate
    tax_amount = round( tax_rate * subtotal / 100, 2)
    tax_total += tax_amount
    tax_list.append( dict( {
      "type": tax_type, 
      "rate": tax_rate,
      "amount": tax_amount,
    }) )

  grand_total = subtotal + tax_total
  print( tax_list )

  return dict(
    subtotal=subtotal,
    tax_list=tax_list,
    tax=tax_total,
    grand_total=grand_total
  )
