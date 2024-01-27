from django.urls import include, path

from . import views

urlpatterns = [
  path( 'registerUser/', views.register_user, name='register_user' ),
  path( 'registerVendor/', views.register_vendor, name='register_vendor' ),
  path( 'login/', views.login, name='login' ),
  path( 'logout/', views.logout, name='logout' ),
  path( 'custDashboard/', views.cust_dashboard, name='cust_dashboard' ),
  path( 'vendDashboard/', views.vend_dashboard, name='vend_dashboard' ),
  path( 'myAccount/', views.my_account, name='my_account' ),
  path( 'activate/<uidb644>/<token>/', views.activate, name='activate' ),
  path( 'forgotPassword/', views.forgot_password, name='forgot_password' ),
  path( 'resetPasswordValidate/<uidb64>/<token>/', views.reset_password_validate, name='reset_password_validate' ),
  path( 'resetPassword/', views.reset_password, name='reset_password' ),
  path( 'vendor/', include( 'vendor.urls' )),
  path( 'customer/', include( 'customers.urls' )),
]
