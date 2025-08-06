# etl/urls.py

from django.urls import path
from . import views

app_name = 'etl'

urlpatterns = [
    path('', views.ETLUploadView.as_view(), name='upload'),
]
