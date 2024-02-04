from django.urls import include, path

from . import views

urlpatterns = [
  path( 'place_orders/', views.place_order, name='place_order' ),
  path( 'payments/', views.payments, name='payments' ),
]