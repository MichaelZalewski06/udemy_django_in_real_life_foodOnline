from django.urls import path

from accounts import views as account_views
from . import views

urlpatterns = [
  path( '', account_views.cust_dashboard, name='customer' ),
  path( 'profile', views.cprofile, name='cprofile' ),
  path( 'my_orders', views.my_orders, name='my_orders' ),
  path( 'order_detail/<int:order_number>', views.order_detail, name='order_detail' ),
]
