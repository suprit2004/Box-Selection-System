from django.urls import path
from fulfillment import views

urlpatterns = [
    path('', views.order_create, name='home'),
    path('products/', views.product_list_create, name='product_list_create'),
    path('boxes/', views.box_list_create, name='box_list_create'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/new/', views.order_create, name='order_create'),
    path('orders/<int:order_id>/recommendation/', views.order_recommendation, name='order_recommendation'),
    path('seed-sample-data/', views.seed_sample_data, name='seed_sample_data'),
]

