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

def send_verification_email( request, user, email_subject, email_template ):
  from_email = settings.DEFAULT_FROM_EMAIL
  current_site = get_current_site( request )
  message = render_to_string( email_template, {
    'user': user,
    'domain': current_site,
    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
    'token': default_token_generator.make_token(user),
  })
  print( f"message={message}" )
  to_email = user.email
  mail = EmailMessage( email_subject, message, from_email, to=[to_email] )
  mail.content_subtype = "html"
  mail.send()

