from django.urls import path
from . import views


urlpatterns = [
    path('shop-publish/<int:shop_id>/<int:book_id>/',
         views.ShopPublishView.as_view(),
         name='depot_shop_publish'
    )
]
