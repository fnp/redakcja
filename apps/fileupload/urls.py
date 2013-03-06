from django.conf.urls.defaults import *
from fileupload.views import UploadView

urlpatterns = patterns('',
    (r'^(?P<path>.+)$', UploadView.as_view(), {}, 'upload'),
)

