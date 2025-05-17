from django.urls import path
from .views import update_order_status, vendor_logout, vendor_register, vendor_login,vendor_dashboard, vendor_food_list, vendor_add_food, vendor_order_list,vendor_edit_food,vendor_delete_food

urlpatterns = [
    path('vendor_register', vendor_register, name='vendor_register'),
    path('vendor_login', vendor_login, name='vendor_login'),
     path('vendor_dashboard', vendor_dashboard, name='vendor_dashboard'),
    path('food_list', vendor_food_list, name='vendor_food_list'),
    path('add_food', vendor_add_food, name='vendor_add_food'),
    path('vendor_order_list', vendor_order_list, name='vendor_order_list'),
     
         path('vendor_edit_food/<int:food_id>/', vendor_edit_food, name='vendor_edit_food'),
    path('vendor_delete_food/<int:food_id>/', vendor_delete_food, name='vendor_delete_food'),



    path('orders/update/<int:order_id>/', update_order_status, name='update_order_status'),


    
    path('vendor_logout', vendor_logout, name='vendor_logout'),
]
