from django.urls import path
from . import views


urlpatterns = [
    path('books/', views.BookList.as_view(),
         name='documents_api_book_list'),
    path('books/<int:pk>/', views.BookDetail.as_view(),
         name='documents_api_book'),
    path('chunks/', views.ChunkList.as_view(),
         name='documents_api_chunk_list'),
    path('chunks/<int:pk>/', views.ChunkDetail.as_view(),
         name='documents_api_chunk'),
    path('chunks/<int:pk>/revisions/', views.ChunkRevisionList.as_view(),
         name='documents_api_chunk_revision_list'),
    path('revisions/<int:pk>/', views.RevisionDetail.as_view(),
         name='documents_api_revision'),
]
