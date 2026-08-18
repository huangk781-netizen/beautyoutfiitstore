from django.urls import path

from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/', views.cart_add, name='cart_add'),
    path('increase/<int:variant_id>/', views.cart_increase, name='cart_increase'),
    path('decrease/<int:variant_id>/', views.cart_decrease, name='cart_decrease'),
    path('remove/<int:variant_id>/', views.cart_remove, name='cart_remove'),
]
