from django.urls import path
from . import views


urlpatterns = [
    path(
        'legimi-publish/<int:book_id>/',
        views.LegimiPublishView.as_view(),
        name='depot_legimi_publish'
    )
]
