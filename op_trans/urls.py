from django.contrib import admin
from django.urls import path

from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ping/', views.ping, name="ping"),
    path('info/', views.info, name="info"),
    path('mutations/', views.mutations, name="mutations"),
    path('conversations/', views.conversations, name="conversations"),
]
