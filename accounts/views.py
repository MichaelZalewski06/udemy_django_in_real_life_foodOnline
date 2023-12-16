from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.http import urlsafe_base64_decode

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator

from .forms import UserForm
from .models import User, UserProfile
from .utils import detect_user, send_verification_email
from vendor.models import Vendor

from vendor.forms import VendorForm

def check_role_vendor( user ):
  if user.role == User.VENDOR:
    return True
  else:
    raise PermissionDenied

def check_role_customer( user ):
  if user.role == User.CUSTOMER:
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

      email_subject = 'Activate Your Account'
      email_template = 'accounts/emails/account_verification_email.html'
      send_verification_email( request, user, email_subject, email_template )

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
    if form.is_valid() and v_form.is_valid():
      first_name = form.cleaned_data[ 'first_name' ]
      last_name = form.cleaned_data[ 'last_name' ]
      username = form.cleaned_data[ 'username' ]
      email = form.cleaned_data[ 'email' ]
      password = form.cleaned_data[ 'password' ]
      user = User.objects.create_user( 
        first_name, last_name, username, email, password 
      )
      user.role = User.VENDOR
      user.save()
      vendor = v_form.save( commit=False )
      vendor.user = user
      user_profile = UserProfile.objects.get( user=user )
      vendor.user_profile = user_profile
      vendor.save()

      email_subject = 'Activate Your Account'
      email_template = 'accounts/emails/account_verification_email.html'
      send_verification_email( request, user )

      messages.success( request, 'Your account has been registered successfully! Please wait for the approval.' )
      return redirect( 'register_vendor' )
    else:
      pass
  else:
    form = UserForm()
    v_form = VendorForm()

  context = {
    'form': form,
    'v_form': v_form,
  }
  return render( request, 'accounts/registerVendor.html', context )

def activate( request, uidb64, token ):
  try:
    uid = urlsafe_base64_decode( uidb64 ).decode()
    user = User._default_manager.get( pk=uid )
  except( TypeError, ValueError, OverflowError, User.DoesNotExist ):
    user = None
  
  if user is not None and default_token_generator.check_token( user, token ):
    user.is_active = True
    user.save()
    messages.succes( request, 'Congratulations! Your account is activated.' )
  else:
    messages.error( request, 'Invalid activation link' )
  return redirect( 'my_account' )

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
  vendor = Vendor.objects.get( user=request.user )
  context = {
    'vendor': vendor,
  }
  return render( request, 'accounts/vendDashboard.html', context )

def forgot_password( request ):
  if request.method == 'POST':
    email = request.POST[ 'email' ]
    if User.objects.filter( email=email ).exists():
      user = User.objects.get( email__exact=email )
      email_subject = 'Reset Your Password'
      email_template = 'accounts/emails/reset_password_email.html'
      send_verification_email( request, user, email_subject, email_template )
      messages.success( request, 'Password reset link has been sent to your email address' )
      return redirect( 'login' )
    else:
      messages.error( request, 'Account does not exist' )
      return redirect( 'forgot_password' )

  return render( request, 'accounts/forgot_password.html' )

def reset_password_validate( request, uidb64, token ):
  try:
    uid = urlsafe_base64_decode( uidb64 ).decode()
    user = User._default_manager.get( pk=uid )
  except( TypeError, ValueError, OverflowError, User.DoesNotExist ):
    user = None

  if user is not None and default_token_generator.check_token( user, token ):
    request.session[ 'uid' ] = uid
    messages.info(request, 'Please reset your password' )
    return redirect( 'reset_password' )
  else:
    messages.error(request, 'This link has been expired!')
    return redirect( 'my_account' )

def reset_password( request ):
  if request.method == 'POST':
    password = request.POST[ 'password' ]
    confirm_password = request.POST[ 'confirm_password' ]
    if password == confirm_password:
      pk = request.session.get( 'uid' )
      user = User.objects.get( pk=pk )
      user.set_password( password )
      user.is_active = True
      user.save()
      messages.success( request, 'Password reset successful' )
      return redirect( 'login' )
    else:
      messages.error( request, 'Passwords do not match' )
      return redirect( 'reset_password' )
  return render( request, 'accounts/reset_password.html' )
