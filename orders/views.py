from django.http import HttpResponse
from django.shortcuts import redirect, render

import simplejson as json

from marketplace.context_processors import get_cart_totals
from marketplace.models import Cart

from .forms import OrderForm
from .models import Order
from .utils import generate_order_number

# Create your views here.
def place_order( request ):
  cart_items = Cart.objects.filter( user=request.user ).order_by( 'created_at' )
  cart_count = cart_items.count()
  if cart_count <= 0:
    return redirect( 'marketplace' )

  subtotal = get_cart_totals( request )[ 'subtotal' ]
  total_tax = get_cart_totals( request )[ 'tax' ]
  grand_total = get_cart_totals( request )[ 'grand_total' ]
  tax_data = get_cart_totals( request )[ 'tax_list' ]

  if request.method == 'POST':
    form = OrderForm( request.POST )
    if form.is_valid():
      order = Order()
      order.first_name = form.cleaned_data[ 'first_name' ]
      order.last_name = form.cleaned_data[ 'last_name' ]
      order.phone = form.cleaned_data[ 'phone' ]
      order.email = form.cleaned_data[ 'email' ]
      order.address = form.cleaned_data[ 'address' ]
      order.city = form.cleaned_data[ 'city' ]
      order.state = form.cleaned_data[ 'state' ]
      order.country = form.cleaned_data[ 'country' ]
      order.pin_code = form.cleaned_data[ 'pin_code' ]

      order.total = grand_total
      order.tax_data = json.dumps(tax_data)
      order.total_tax = total_tax
      order.subtotal = subtotal
      order.payment_method = request.POST[ 'payment_method' ]
      order.save()
      order.order_number = generate_order_number( order.id )
      order.save()
      context = {
        'order': order,
        'cart_items': cart_items,
      }
      return render( request, 'orders/place_order.html', context )
    else:
      print( form.errors )

  return( render( request, 'orders/place_order.html' ))

def payments( request ):
  order_number = request.POST.get( 'order_number' )
  transaction_id = request.POST.get( 'transaction_id' )
  payment_method = request.POST.get( 'payment_method' )
  status = request.POST.get( 'status' )

  order = Order.objects.get( user=request.user, order_number=order_number )
  payment = Payment(
   user=request.user,
   transaction_id = transaction_id,
   payment_method = payment_method,
   amount = order.total,
   status = status,
  )
  payment.save()

  order.payment = payment
  order.is_ordered = True
  order.save()

  

  return HttpResponse( 'Payments View' )

