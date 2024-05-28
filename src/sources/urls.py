from django.urls import path
from . import views


urlpatterns = [
    path('source/<int:pk>/', views.SourceView.as_view(), name='source'),
    path('upload/<int:sid>/', views.SourceUploadView.as_view(), name='source_upload'),
    path('prepare/book/<int:pk>/', views.prepare, name='source_book_prepare'),
]
