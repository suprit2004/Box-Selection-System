from django.urls import path
from fulfillment import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('home/', views.dashboard, name='home'),
    
    # Products
    path('products/', views.product_list_create, name='product_list_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Shipping Boxes
    path('boxes/', views.box_list_create, name='box_list_create'),
    path('boxes/<int:pk>/edit/', views.box_edit, name='box_edit'),
    path('boxes/<int:pk>/delete/', views.box_delete, name='box_delete'),
    
    # Orders & Recommendations
    path('orders/', views.order_list, name='order_list'),
    path('orders/new/', views.order_create, name='order_create'),
    path('orders/<int:order_id>/recommendation/', views.order_recommendation, name='order_recommendation'),
    
    # Fixture seed
    path('seed-sample-data/', views.seed_sample_data, name='seed_sample_data'),
]
