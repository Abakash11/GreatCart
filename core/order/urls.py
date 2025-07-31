from django.urls import path
from . import views

urlpatterns=[
    path('place-order',views.place_order,name='place_order'),
    path('payments',views.payments,name='payments'),
    path('order-complite/',views.order_complite,name='order_complite')

]