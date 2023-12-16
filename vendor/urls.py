from django.urls import path

from accounts import views as account_views
from . import views

urlpatterns = [
  path( '', account_views.vend_dashboard, name='vendor' ),
  path( 'profile', views.vprofile, name='vprofile' ),
]
