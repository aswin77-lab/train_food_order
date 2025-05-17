
from django.urls import path
from .views import  admin_login,admin_dashboard,add_train_route,add_station, approve_vendor, disapprove_vendor, orders_list,train_list,user_list,admin_logout,delete_user, vendor_list

urlpatterns = [
    path('admin_login', admin_login, name='admin_login'),
    path('admin_dashboard', admin_dashboard, name='admin_dashboard'),
    path('add_train_route', add_train_route, name='add_train_route'),
    path('add_station', add_station, name='add_station'),
    path('train_list', train_list, name='train_list'),
    path('user_list', user_list, name='user_list'),
    path('delete_user/<int:user_id>/', delete_user, name='delete_user'),
     path("vendors", vendor_list, name="vendor_list"),
    path("vendors/approve/<int:vendor_id>/", approve_vendor, name="approve_vendor"),
    path("vendors/disapprove/<int:vendor_id>/", disapprove_vendor, name="disapprove_vendor"),
    path('orders', orders_list, name='orders_list'),



    path('admin_logout', admin_logout, name='admin_logout'),

]
