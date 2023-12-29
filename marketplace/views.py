from django.db.models import Prefetch, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from django.contrib.auth.decorators import login_required

from .context_processors import get_cart_count, get_cart_totals
from .models import Cart
from menu.models import Category, FoodItem
from vendor.models import Vendor

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
  if request.user.is_authenticated:
    cart_items = Cart.objects.filter( user=request.user )
  else:
    cart_items = None

  context = {
    'cart_items': cart_items,
    'categories': categories,
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
  vendors = Vendor.objects.filter(
      Q( id__in=vendors_have_food ) 
    | Q( 
        vendor_name__icontains=keyword, 
        is_approved=True, user__is_active=True 
      )
  )
  vendor_count = vendors.count()
  context = {
    'vendors': vendors,
    'vendor_count': vendor_count,
  }
  return render( request, 'marketplace/listings.html', context )