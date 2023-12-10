from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect, render

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import UserForm
from .models import User, UserProfile
from .utils import detect_user

from vendor.forms import VendorForm

def check_role_vendor( user ):
  if user.role == Customer.VENDOR:
    return True
  else:
    raise PermissionDenied

def check_role_customer( user ):
  if user.role == Customer.CUSTOMER:
    return True
  else:
    raise PermissionDenied

# Create your views here.
def register_user( request ):
  if request.user.is_authenticated:
    messages.warning( request, 'You are already logged in')
    return redirect( 'my_account' )
  elif request.method == 'POST':
    form = UserForm( request.POST )
    if form.is_valid():
      # Create the user using the form
      # password = form.cleaned_data( 'password' )
      # user = form.save( commit=False )
      # user.set_password( password )
      # user.role = User.CUSTOMER
      # form.save()

      # Create the user using create_user method
      first_name = form.cleaned_data[ 'first_name' ]
      last_name = form.cleaned_data[ 'last_name' ]
      username = form.cleaned_data[ 'username' ]
      email = form.cleaned_data[ 'email' ]
      password = form.cleaned_data[ 'password' ]
      user = User.objects.create_user( 
        first_name, last_name, username, email, password 
      )
      user.role = User.CUSTOMER
      user.save()
      messages.success( request, 'Your account has been registered successfully!' )
      return redirect( 'register_user' )
  else:
    form = UserForm()

  context = {
    'form': form,
  }
  return render( request, 'accounts/registerUser.html', context )

def register_vendor( request ):
  if request.user.is_authenticated:
    messages.warning( request, 'You are already logged in')
    return redirect( 'my_account' )
  elif request.method == "POST":
    form = UserForm( request.POST )
    v_form = VendorForm( request.POST, request.FILES )
    print( f"form.is_valid={form.is_valid()}, v_form.is_valid={v_form.is_valid()}")
    if form.is_valid() and v_form.is_valid():
      first_name = form.cleaned_data[ 'first_name' ]
      last_name = form.cleaned_data[ 'last_name' ]
      username = form.cleaned_data[ 'username' ]
      email = form.cleaned_data[ 'email' ]
      password = form.cleaned_data[ 'password' ]
      user = User.objects.create_user( 
        first_name, last_name, username, email, password 
      )
      print( "User created")
      user.role = User.VENDOR
      user.save()
      vendor = v_form.save( commit=False )
      vendor.user = user
      user_profile = UserProfile.objects.get( user=user )
      vendor.user_profile = user_profile
      vendor.save()

      messages.success( request, 'Your account has been registered successfully! Please wait for the approval.' )
      return redirect( 'register_vendor' )
    else:
      print( f"form.errors={form.errors}" )
      print( f"v_form.errors={v_form.errors}")

  else:
    form = UserForm()
    v_form = VendorForm()

  context = {
    'form': form,
    'v_form': v_form,
  }
  return render( request, 'accounts/registerVendor.html', context )

def login( request ):
  if request.user.is_authenticated:
    messages.warning( request, 'You are already logged in')
    return redirect( 'my_account' )
  elif request.method == "POST":
    email = request.POST[ 'email' ]
    password = request.POST[ 'password' ]
    user = auth.authenticate( email=email, password=password )
    if user is not None:
      auth.login( request, user )
      messages.success( request, 'You are now logged in' )
      return redirect( 'my_account' )
    else:
      messages.error( request, 'Invalid login credentials' )
      return redirect( 'login' )
  return render( request, 'accounts/login.html')

def logout( request ):
  auth.logout( request )
  messages.info( request, 'You are logged out' )
  return redirect( 'login' )

@login_required( login_url='login' )
def my_account( request ):
  user = request.user
  redirect_url = detect_user( user )
  return redirect( redirect_url )

@login_required( login_url='login' )
@user_passes_test( check_role_customer )
def cust_dashboard( request ):
  return render( request, 'accounts/custDashboard.html' )

@login_required( login_url='login' )
@user_passes_test( check_role_vendor )
def vend_dashboard( request ):
  return render( request, 'accounts/vendDashboard.html' )
