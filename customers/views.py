from django.shortcuts import get_object_or_404, redirect, render

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

import simplejson as json

from accounts.forms import UserInfoForm, UserProfileForm
from accounts.models import UserProfile
from accounts.views import check_role_customer

from orders.models import Order, OrderedFood

# Create your views here.

@login_required( login_url='login' )
@user_passes_test( check_role_customer )
def cprofile( request ):
  profile = get_object_or_404( UserProfile, user=request.user )
  if request.method == 'POST':
    profile_form = UserProfileForm( request.POST, request.FILES, instance=profile )
    user_form = UserInfoForm( request.POST, instance=request.user )
    if profile_form.is_valid() and user_form.is_valid():
      profile_form.save()
      user_form.save()
      messages.success( request, 'Profile updated' )
      return redirect( 'cprofile' )
  else:
    profile_form = UserProfileForm( instance=profile )
    user_form = UserInfoForm( instance=request.user )

  context = {
    'profile': profile,
    'profile_form': profile_form,
    'user_form': user_form,
  }
  return render( request, 'customers/cprofile.html', context )

def my_orders( request ):
  orders = Order.objects.filter( user=request.user, is_ordered=True ).order_by( 'created_at' )
  context = {
    'orders': orders,
  }
  return render( request, 'customers/my_orders.html', context )

def order_detail( request, order_number ):
  try:
    order = Order.objects.get( order_number=order_number, is_ordered=True )
    ordered_food = OrderedFood.objects.filter( order=order )
    print( ordered_food )
    subtotal = 0
    for item in ordered_food:
      subtotal += (item.price * item.quantity)
      print( f'subtotal={subtotal}' )
    tax_data = json.loads( order.tax_data )
    context = {
      'order': order,
      'ordered_food': ordered_food,
      'subtotal': subtotal,
      'tax_data': tax_data,
    }
    return render( request, 'customers/order_detail.html', context )
  except Exception as e:
    print( e )
    return redirect( 'customer' )