from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings


admin.autodiscover()


urlpatterns = patterns('',
    # Example:
    # (r'^platforma/', include('platforma.foo.urls')),

    # Admin panel
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/(.*)', admin.site.root),
)


# Static files
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^%s(?P<path>.+)$' % settings.MEDIA_URL[1:], 'django.views.static.serve', 
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        url(r'^%s(?P<path>.+)$' % settings.STATIC_URL[1:], 'django.views.static.serve',
            {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
    )
