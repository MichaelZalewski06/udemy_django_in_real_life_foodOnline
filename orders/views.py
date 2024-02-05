from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from django.contrib.auth.decorators import login_required

import simplejson as json

from accounts.utils import send_notification

from marketplace.context_processors import get_cart_totals
from marketplace.models import Cart

from .forms import OrderForm
from .models import Order, OrderedFood, Payment
from .utils import generate_order_number

# Create your views here.
@login_required( login_url='login' )
def place_order( request ):
  cart_items = Cart.objects.filter( user=request.user ).order_by( 'created_at' )
  cart_count = cart_items.count()
  if cart_count <= 0:
    return redirect( 'marketplace' )

  vendors_ids = []
  for i in cart_items:
    if i.food_item.vendor.id not in vendors_ids:
      vendors_ids.append(i.food_item.vendor.id)

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
      order.user = request.user

      order.total = grand_total
      order.tax_data = json.dumps(tax_data)
      order.total_tax = total_tax
      order.subtotal = subtotal
      order.payment_method = request.POST[ 'payment_method' ]
      order.save()
      order.order_number = generate_order_number( order.id )
      order.vendors.add(*vendors_ids)

      order.save()
      context = {
        'order': order,
        'cart_items': cart_items,
      }
      return render( request, 'orders/place_order.html', context )
    else:
      print( form.errors )

  return( render( request, 'orders/place_order.html' ))

@login_required( login_url='login' )
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

  cart_items = Cart.objects.filter( user=request.user )
  for item in cart_items:
    ordered_food = OrderedFood()
    ordered_food.order = order
    ordered_food.payment = payment
    ordered_food.user = request.user
    ordered_food.fooditem = item.food_item
    ordered_food.quantity = item.quantity
    ordered_food.price = item.food_item.price
    ordered_food.amount = item.food_item.price * item.quantity
    ordered_food.save()

  mail_subject = 'Thank you for ordering with us.'
  mail_template = 'orders/order_confirmation_email.html'
  context = {
    'user': request.user,
    'order': order,
    'to_email': order.email,
  }
  send_notification( mail_subject, mail_template, context )

  mail_subject = 'You have received a new order.'
  mail_template = 'orders/new_order_received.html'
  to_emails = []
  for i in cart_items:
    vendor_email = i.food_item.vendor.user.email
    if vendor_email not in to_emails:
      to_emails.append( vendor_email )
  context = {
    'user': request.user,
    'order': order,
    'to_email': to_emails,
  }
  send_notification( mail_subject, mail_template, context )

  cart_items.delete()

  response = {
    'order_number': order_number,
    'transaction_id': transaction_id,
  }
  return JsonResponse(  response )

def order_complete( request ):
  order_number = request.GET.get( 'order_no' )
  transaction_id = request.GET.get( 'trans_id' )

  context = {}
  try:
    order = Order.objects.get( user=request.user, payment__transaction_id=transaction_id, is_ordered=True )
    ordered_food = OrderedFood.objects.filter( order=order )

    subtotal = 0
    for item in ordered_food:
      subtotal += (item.price * item.quantity)
    tax_data = json.loads( order.tax_data )

    context = {
      'order': order,
      'order_number': order_number,
      'ordered_food': ordered_food,
      'subtotal': subtotal,
      'tax_data': tax_data,
      'transaction_id': transaction_id,
    }
  except:
    return redirect( 'home' )
  return render( request, 'orders/order_complete.html', context )
