from django.urls import include, path
from . import views


urlpatterns = [
    path('documents/', include('documents.api.urls')),

    path('me/', views.MeView.as_view()),
]
