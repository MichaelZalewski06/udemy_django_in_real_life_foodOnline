from django.urls import path

from . import views

urlpatterns = [
  path( 'registerUser/', views.register_user, name='register_user' ),
  path( 'registerVendor/', views.register_vendor, name='register_vendor' ),
  path( 'login/', views.login, name='login' ),
  path( 'logout/', views.logout, name='logout' ),
  path( 'custDashboard/', views.cust_dashboard, name='cust_dashboard' ),
  path( 'vendDashboard/', views.vend_dashboard, name='vend_dashboard' ),
  path( 'myAccount/', views.my_account, name='my_account' ),
]
