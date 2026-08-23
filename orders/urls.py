from django.urls import path

from . import views
from .store_pickup import checkout

app_name = 'orders'

urlpatterns = [
    path('checkout/', checkout, name='checkout'),
    path('checkout/<int:order_id>/done/', views.checkout_done, name='checkout_done'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/request-return/', views.order_request_return, name='order_request_return'),
    path('dashboard/', views.sales_dashboard, name='sales_dashboard'),
]
