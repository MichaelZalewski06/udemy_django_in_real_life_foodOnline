from django.conf import settings
from django.core.mail import EmailMessage, message
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site

def detect_user( user ):
  if user.role == 1:
    redirect_url = 'vend_dashboard'
  elif user.role == 2:
    redirect_url = 'cust_dashboard'
  elif user.role == None and user.is_superadmin:
    redirect_url = '/admin'
  return redirect_url