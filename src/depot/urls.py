from django.urls import path
from . import views


urlpatterns = [
    path('site-publish/<int:site_id>/<int:book_id>/',
         views.SitePublishView.as_view(),
         name='depot_site_publish'
    )
]
