from django.urls import path
from . import views


urlpatterns = [
    path('wl2html.xsl', views.XslView.as_view()),
    path('wl.css', views.EditorCSS.as_view()),

    path('tags/', views.TagsView.as_view(), name='wlxml_tags'),
    path('tags/<slug>/', views.TagView.as_view(), name='wlxml_tag'),
]
