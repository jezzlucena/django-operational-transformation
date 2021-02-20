from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin

from app import views as app_views
from op_trans import views as op_trans_views

urlpatterns = [
    url(r'^reset/$', app_views.reset, name="reset"),
    url(r'^ping/$', app_views.ping, name="ping"),
    url(r'^info/$', app_views.info, name="info"),
    url(r'^mutations/$', app_views.mutations, name="mutations"),
    url(r'^conversations/$', app_views.conversations, name="conversations"),
    url(r'^$', op_trans_views.index, name="home"),
]
