from django.conf.urls import patterns, url
from fileupload.views import UploadView

urlpatterns = patterns('',
    url(r'^(?P<path>(?:.*/)?)$', UploadView.as_view(), name='fileupload'),
)

