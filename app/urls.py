

from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path

from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('op_trans.urls')),
    path('v1/', views.index, name="conversations"),
    path('v2/', views.frontend, name="frontend"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
