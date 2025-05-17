
from django.urls import path
from .views import search_food_by_pnr, trip_book, trip_search_results, user_dashboard, user_login, user_logout, user_order_list, user_register,trip_detail, vendor_food_detail,order_food

urlpatterns = [
    path('user_register', user_register, name='user_register'),
     path('user_login', user_login, name='user_login'),
    path('user_logout', user_logout, name='user_logout'),
    path('user_dashboard', user_dashboard, name='user_dashboard'),
    path('trip_search_results', trip_search_results, name='trip_search_results'),
    path('book/<int:route_id>/', trip_book, name='trip_book'),

    path('trip_detail', trip_detail, name='trip_detail'),  
    path('search_food_by_pnr', search_food_by_pnr, name='search_food_by_pnr'),
    path('vendor_food_detail/<int:vendor_id>/food/', vendor_food_detail, name='vendor_food_detail'),
    path('order_food/<int:food_id>/food/', order_food, name='order_food'),
  path('user_order_list', user_order_list, name='user_order_list'),

]
