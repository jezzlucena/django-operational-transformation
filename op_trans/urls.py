from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.urls import re_path

from app import views as app_views
# from op_trans import views as op_trans_views

urlpatterns = [
    re_path('admin/', admin.site.urls),
    re_path('reset/?$', app_views.reset, name="reset"),
    re_path('ping/?$', app_views.ping, name="ping"),
    re_path('info/?$', app_views.info, name="info"),
    re_path('mutations/?$', app_views.mutations, name="mutations"),
    re_path('conversations/?$', app_views.conversations, name="conversations"),
    re_path('/?$', op_trans_views.info, name="home"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
