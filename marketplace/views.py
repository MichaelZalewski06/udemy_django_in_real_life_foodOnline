from datetime import date

from django.db.models import Prefetch, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from django.contrib.auth.decorators import login_required
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D

from .context_processors import get_cart_count, get_cart_totals
from .models import Cart
from accounts.models import UserProfile
from menu.models import Category, FoodItem
from orders.forms import OrderForm
from vendor.models import OpeningHour, Vendor

# Create your views here.
def marketplace( request ):
  vendors = Vendor.objects.filter( is_approved=True, user__is_active=True )
  vendor_count = vendors.count()
  context = {
    'vendors': vendors,
    'vendor_count': vendor_count,
  }
  return render( request, 'marketplace/listings.html', context )

def vendor_detail( request, vendor_slug ):
  vendor = get_object_or_404( Vendor, vendor_slug=vendor_slug )
  categories = Category.objects.filter( vendor=vendor ).prefetch_related(
    Prefetch(
      'fooditems',
      queryset = FoodItem.objects.filter( is_available=True )
    )
  )

  hours = OpeningHour.objects.filter( vendor=vendor )
  today = date.today()
  weekday = today.isoweekday()
  current_hours = OpeningHour.objects.filter( vendor=vendor, day=weekday )
  is_open = vendor.is_open()

  if request.user.is_authenticated:
    cart_items = Cart.objects.filter( user=request.user )
  else:
    cart_items = None

  context = {
    'cart_items': cart_items,
    'categories': categories,
    'current_hours': current_hours,
    'hours': hours,
    'vendor': vendor,
  }
  return render( request, 'marketplace/vendor_detail.html', context )

def add_to_cart( request, food_id=None ):
  print( f'remove_cart food_id={food_id}')
  if not request.user.is_authenticated:
    return JsonResponse({
      'status': 'login',
      'message': 'You must be logged in',
    })

  try:
    food = FoodItem.objects.get( id=food_id )
  except:
    return JsonResponse({
      'status': 'failed',
      'message': f'Food Item {food_id} does not exist.',
    })

  try:
    cart = Cart.objects.get( user=request.user, food_item=food )
    cart.quantity += 1
  except:
    cart = Cart.objects.create(
      user = request.user,
      food_item = food,
      quantity = 1,
    )
  cart.save()
  return JsonResponse({
    'status': 'success',
    'message': f'Food Item {food_id} qty {cart.quantity} added to cart.',
    'cart_counter': get_cart_count( request ),
    'cart_totals': get_cart_totals( request ),
    'qty': cart.quantity,
  })

def decrease_cart( request, food_id=None ):
  if not request.user.is_authenticated:
    return JsonResponse({
      'status': 'login',
      'message': 'You must be logged in',
    })

  try:
    food = FoodItem.objects.get( id=food_id )
  except:
    return JsonResponse({
      'status': 'failed',
      'message': f'Food Item {food_id} does not exist.',
    })

  try:
    cart = Cart.objects.get( user=request.user, food_item=food )
    cart.quantity -= 1
  except:
    return JsonResponse({
      'status': 'failed',
      'message': f'Item { food_id } does not exist in cart',
    })
  
  if cart.quantity <= 0:
    cart.delete()
    cart.quantity = 0
  else:
    cart.save()

  return JsonResponse({
    'status': 'success',
    'message': f'Food Item {food_id} qty {cart.quantity} added to cart.',
    'cart_counter': get_cart_count( request ),
    'cart_totals': get_cart_totals( request ),
    'qty': cart.quantity,
  })

def delete_cart( request, cart_id=None ):
  if not request.user.is_authenticated:
    return JsonResponse({
      'status': 'login',
      'message': 'You must be logged in',
    })

  try:
    cart_item = Cart.objects.get( id=cart_id )
    print( f'delete_cart cart_id={cart_id}')
    if cart_item:
      cart_item.delete()
      print( f'delete_cart cart_id={cart_id}')
      return JsonResponse({
        'status': 'success',
        'message': f'Item removed from cart.',
        'cart_counter': get_cart_count( request ),
        'cart_totals': get_cart_totals( request ),
      })
  except:
    return JsonResponse({
      'status': 'failed',
      'message': f'Cart Item {cart_id} does not exist.',
    })

@login_required( login_url='login' )
def cart( request ):
  cart_items = Cart.objects.filter( user=request.user ).order_by( 'created_at' )
  context = {
    'cart_items': cart_items
  }
  return render( request, 'marketplace/cart.html', context )

def search( request ):
  if not 'address' in request.GET:
    return redirect( 'marketplace' )

  address = request.GET[ 'address' ]
  keyword = request.GET[ 'keyword' ]
  address = request.GET[ 'address' ]
  lat = request.GET[ 'lat' ]
  lng = request.GET[ 'lng' ]
  radius = request.GET[ 'radius' ]

  vendors_have_food = (
      FoodItem.objects
        .filter( food_title__icontains=keyword, is_available=True )
        .values_list( 'vendor', flat=True )
  )
  q_search_results = (
      Q( id__in=vendors_have_food) 
    | Q(
        vendor_name__icontains=keyword, 
        is_approved=True, user__is_active=True 
      )
  )
  if lat and long and radius:
    pnt = GEOSGeometry( f'POINT({long} {lat})')
    q_search_results = q_search_results & Q( user_profile__location__distance_lte=( pnt, D( km=radius )))
    vendors = (Vendor.objects.filter( q_search_results )
        .annotate(distance=Distance( "user_profile__location", pnt ))
        .order_by("distance")
    )
    for v in vendors:
      v.kms = round(v.distance.km, 1)
  else:
    vendors = Vendor.objects.filter( q_search_results )
  vendor_count = vendors.count()
  context = {
    'vendors': vendors,
    'vendor_count': vendor_count,
    'source_location': address,
  }
  return render( request, 'marketplace/listings.html', context )

@login_required( login_url='login' )
def checkout( request ):
  cart_items = Cart.objects.filter( user=request.user ).order_by( 'created_at' )
  cart_count = cart_items.count()
  if cart_count <= 0:
    return redirect( 'marketplace' )
  user_profile = UserProfile.objects.get( user=request.user )
  initial_values = {
    'first_name': request.user.first_name,
    'last_name': request.user.last_name,
    'phone': request.user.phone_number,
    'email': request.user.email,
    'address': user_profile.address,
    'city': user_profile.city,
    'state': user_profile.state,
    'country': user_profile.country,
    'pin_code': user_profile.pin_code,
  }
  form = OrderForm( initial=initial_values )
  context = {
    'cart_items': cart_items,
    'form': form,
  }
  return render( request, 'marketplace/checkout.html', context )