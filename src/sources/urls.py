from django.urls import path
from . import views


urlpatterns = [
    path('source/<int:pk>/', views.SourceView.as_view(), name='source'),
    path('upload/<int:sid>/', views.SourceUploadView.as_view(), name='source_upload'),
    path('prepare/<int:bsid>/', views.prepare, name='source_book_prepare'),
]
