from django.urls import path
from . import views


urlpatterns = [
    path('', views.isbn_list, name='isbn_list'),
]
