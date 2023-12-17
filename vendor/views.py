from django.shortcuts import get_object_or_404, redirect, render

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import VendorForm
from .models import Vendor

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.views import check_role_vendor

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