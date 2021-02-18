from django.contrib import admin
from django.urls import re_path

from app import views

urlpatterns = [
    re_path('admin/?$', admin.site.urls),
    re_path('ping/?$', views.ping, name="ping"),
    re_path('info/?$', views.info, name="info"),
    re_path('mutations/?$', views.mutations, name="mutations"),
    re_path('conversations/?$', views.conversations, name="conversations"),
]
