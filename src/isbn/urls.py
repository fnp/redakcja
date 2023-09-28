from django.urls import path
from . import views


urlpatterns = [
    path('', views.isbn_list, name='isbn_list'),
    path('genarate/<int:document_id>/', views.generate, name='isbn_generate'),
]
