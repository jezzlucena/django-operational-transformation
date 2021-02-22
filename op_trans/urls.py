from django.conf.urls import url
from django.urls import path

from op_trans import views as op_trans_views

urlpatterns = [
    path('reset/', op_trans_views.reset, name="reset"),
    path('ping/', op_trans_views.ping, name="ping"),
    path('info/', op_trans_views.info, name="info"),
    path('mutations/', op_trans_views.mutations, name="mutations"),
    path('conversations/', op_trans_views.conversations, name="conversations"),
]
