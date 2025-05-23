
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path,include

from train_food_order.views import homepage


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name='homepage'),
    path('users/', include('users.urls')),
    path('superadmin/', include('superadmin.urls')),
     path('vendors/', include('vendors.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)