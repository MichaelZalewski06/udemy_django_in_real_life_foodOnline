from django.shortcuts import get_object_or_404, redirect, render

from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.template.defaultfilters import slugify

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import OpeningHourForm, VendorForm
from .models import OpeningHour, Vendor

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.views import check_role_vendor

from menu.forms import CategoryForm, FoodItemForm
from menu.models import Category, FoodItem

from orders.models import Order, OrderedFood

def get_vendor( request ):
  return Vendor.objects.get( user=request.user )

# Create your views here.
@login_required( login_url='login' )
@user_passes_test( check_role_vendor )
def vprofile( request ):
  profile = get_object_or_404( UserProfile, user=request.user )
  vendor = get_object_or_404( Vendor, user=request.user )

  if request.method == 'POST':
    profile_form = UserProfileForm( request.POST, request.FILES, instance=profile )
    vendor_form = VendorForm( request.POST, request.FILES, instance=vendor )
    if profile_form.is_valid() and vendor_form.is_valid():
      profile_form.save()
      vendor_form.save()
      messages.success( request, 'Settings updated.')
      return redirect( 'vprofile' )
    else:
      print( f'profile.errors={profile_form.errors}')
      print( f'vendor.errors={vendor_form.errors}')

  else:
    profile_form = UserProfileForm( instance=profile )
    vendor_form = VendorForm( instance=vendor )
  context = {
    'profile': profile,
    'profile_form': profile_form,
    'vendor': vendor,
    'vendor_form': vendor_form,
  }
  return render( request, 'vendor/vprofile.html', context )

@login_required( login_url='login' )
@user_passes_test( check_role_vendor )
def menu_builder( request ):
  vendor = get_vendor( request )
  categories = Category.objects.filter( vendor=vendor ).order_by( 'created_at' )
  context = {
    'categories': categories,
  }
  return render( request, 'vendor/menu_builder.html', context )

@login_required( login_url='login' )
@user_passes_test( check_role_vendor )
def fooditems_by_category( request, pk=None ):
  vendor = get_vendor( request )
  category = get_object_or_404( Category, pk=pk )
  fooditems = FoodItem.objects.filter( category=category )
  context = {
    'fooditems': fooditems,
    'category': category,
  }
  return render( request, 'vendor/fooditems_by_category.html', context )

@login_required( login_url='login' )
@user_passes_test( check_role_vendor )
def add_category( request ):
  if request.method == 'POST':
    form = CategoryForm( request.POST )
    if form.is_valid():
      category_name = form.cleaned_data[ 'category_name' ]
      category = form.save( commit=False )
      category.vendor = get_vendor( request )
      category.slug = slugify( category_name ) + '-' + str( category.vendor.id )
      form.save()
      messages.success( request, 'Category added successfully' )
      return redirect( 'menu_builder' )
  else:
    form = CategoryForm()
  context = {
    'form': form,
  }
  return render( request, 'vendor/add_category.html', context )

@login_required( login_url='login' )
@user_passes_test( check_role_vendor )
def edit_category( request, pk=None ):
  category = get_object_or_404( Category, pk=pk )
  if request.method == 'POST':
    form = CategoryForm( request.POST, instance=category )
    if form.is_valid():
      category_name = form.cleaned_data[ 'category_name' ]
      category = form.save( commit=False )
      category.vendor = get_vendor( request )
      category.slug = slugify( category_name ) + '-' + str( category.vendor.id )
      form.save()
      messages.success( request, 'Category updated successfully' )
      return redirect( 'menu_builder' )
  else:
    form = CategoryForm( instance=category )
  context = {
    'category': category,
    'form': form,
  }
  return render( request, 'vendor/edit_category.html', context )

@login_required( login_url='login' )
@user_passes_test( check_role_vendor )
def delete_category( request, pk=None ):
  category = get_object_or_404( Category, pk=pk )
  category.delete()
  messages.success( request, 'Category has been deleted' )
  return redirect( 'menu_builder' )

@login_required( login_url='login' )
@user_passes_test( check_role_vendor )
def add_food( request ):
  if request.method == 'POST':
    form = FoodItemForm( request.POST, request.FILES )
    if form.is_valid():
      food_title = form.cleaned_data[ 'food_title' ]
      food = form.save( commit=False )
      food.vendor = get_vendor( request )
      food.slug = slugify( food_title )
      form.save()
      messages.success( request, 'Food Item added successfully' )
      return redirect( 'fooditems_by_category', food.category.id )
  else:
    form = FoodItemForm()
    form.fields[ 'category' ].queryset = Category.objects.filter( vendor=get_vendor( request ))
  context = {
    'form': form,
  }
  return render( request, 'vendor/add_food.html', context )

@login_required( login_url='login' )
@user_passes_test( check_role_vendor )
def edit_food( request, pk=None ):
  food = get_object_or_404( FoodItem, pk=pk )
  if request.method == 'POST':
    form = FoodItemForm( request.POST, request.FILES, instance=food )
    if form.is_valid():
      food_title = form.cleaned_data[ 'food_title' ]
      food = form.save( commit=False )
      food.vendor = get_vendor( request )
      food.slug = slugify( food_title )
      form.save()
      messages.success( request, 'Food Item updated successfully' )
      return redirect( 'fooditems_by_category', food.category.id )
  else:
    form = FoodItemForm( instance=food )
    form.fields[ 'category' ].queryset = Category.objects.filter( vendor=get_vendor( request ))
  context = {
    'food': food,
    'form': form,
  }
  return render( request, 'vendor/edit_food.html', context )

@login_required( login_url='login' )
@user_passes_test( check_role_vendor )
def delete_food( request, pk=None ):
  food = get_object_or_404( FoodItem, pk=pk )
  food.delete()
  messages.success( request, 'Food Item has been deleted' )
  return redirect( 'fooditems_by_category', food.category.id )

@login_required( login_url='login' )
@user_passes_test( check_role_vendor )
def opening_hours( request ):
  opening_hours = OpeningHour.objects.filter( vendor=get_vendor( request ))
  form = OpeningHourForm()
  context = {
    'opening_hours': opening_hours,
    'form': form,
  }
  return render( request, 'vendor/opening_hours.html', context )

@login_required( login_url='login' )
@user_passes_test( check_role_vendor )
def add_opening_hours( request ):
  day = request.POST.get( 'day' )
  from_hour = request.POST.get( 'from_hour' )
  to_hour = request.POST.get( 'to_hour' )
  is_closed = request.POST.get( 'is_closed' ) == 'true'

  try:
    hour = OpeningHour.objects.create(
      vendor=get_vendor( request ),
      day=day,
      from_hour=from_hour,
      to_hour=to_hour,
      is_closed=is_closed,
    )
    day = OpeningHour.objects.get( id=hour.id )
    response = { 
      'status': 'success',
      'id': hour.id,
      'day': day.get_day_display(),
    }
    if day.is_closed:
      response.update({
        'is_closed': 'Closed'
      })
    else:
      response.update({
        'from_hour': hour.from_hour,
        'to_hour': to_hour,
      })
  except IntegrityError as e:
    response = { 
      'status': 'failed',
      'message': f'{from_hour} - {to_hour} alread exists for this day' }
  return JsonResponse( response )

@login_required( login_url='login' )
@user_passes_test( check_role_vendor )
def remove_opening_hours( request, pk=None ):
  hour = get_object_or_404( OpeningHour, pk=pk )
  hour.delete()
  return JsonResponse({
    'status': 'success',
    'id': pk,
  })

def order_detail( request, order_number ):
  try:
    order = Order.objects.get( order_number=order_number, is_ordered=True )
    ordered_food = OrderedFood.objects.filter( order=order, fooditem__vendor=get_vendor( request ))
    context = {
      # 'grand_total': order.get_total_by_vendor()[ 'grand_total' ],
      'order': order,
      'ordered_food': ordered_food,
      # 'subtotal': order.get_total_by_vendor()[ 'subtotal' ],
      # 'tax_data': order.get_total_by_vendor()[ 'tax_data' ],
    }
  except Exception as e:
    print( e )
    return redirect( 'vendor' )
  return render( request, 'vendor/order_detail.html', context )

def my_orders(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('created_at')

    context = {
        'orders': orders,
    }
    return render(request, 'vendor/my_orders.html', context)