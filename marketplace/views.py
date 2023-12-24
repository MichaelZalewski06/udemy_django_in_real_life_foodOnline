from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .context_processors import get_cart_count
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
    'qty': cart.quantity,
  })

def decrease_cart( request, food_id=None ):
  print( f'add_to_cart food_id={food_id}')
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
    'qty': cart.quantity,
  })

def cart( request ):
  return render( request, 'marketplace/cart.html' )