from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.urls import re_path

from app import views

urlpatterns = [
    re_path('admin/', admin.site.urls),
    re_path('reset/?$', views.reset, name="reset"),
    re_path('ping/?$', views.ping, name="ping"),
    re_path('info/?$', views.info, name="info"),
    re_path('mutations/?$', views.mutations, name="mutations"),
    re_path('conversations/?$', views.conversations, name="conversations"),
    re_path('/?$', views.info, name="home"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
