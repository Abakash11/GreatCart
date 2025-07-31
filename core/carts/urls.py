from django.urls import path
from . import views

urlpatterns = [
    path('',views.cart,name='cart'),
    path('add_to_cart/<int:product_id>/',views.add_to_cart,name='add_to_cart'),
    path('add_item_to_cart/<int:product_id>/<str:colour>/<str:size>/',views.add_item_to_cart,name='add_item_to_cart'),
    path('remove_cart/<int:product_id>/<str:colour>/<str:size>/',views.remove_cart,name='remove_cart'),
    path('car_item_delete/<int:product_id>/<str:colour>/<str:size>/',views.car_item_delete,name='car_item_delete'),
    path('check_out/',views.check_out,name='check_out')
]