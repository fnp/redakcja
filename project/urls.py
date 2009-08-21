from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings


admin.autodiscover()


urlpatterns = patterns('',
    # Example:
    url(r'^$', 'explorer.views.file_list', name='file_list'),
    url(r'^file/(?P<path>[^/]+)/$', 'explorer.views.file_xml', name='file_xml'),
    url(r'^html/(?P<path>[^/]+)/$', 'explorer.views.file_html', name='file_html'),
    url(r'^images/(?P<folder>[^/]+)/$', 'explorer.views.folder_images', name='folder_image'),
    url(r'^images/$', 'explorer.views.folder_images', {'folder': '.'}, name='folder_image_ajax'),
    
    url(r'^panels/xmleditor$', 'django.views.generic.simple.direct_to_template', 
        {'template': 'explorer/panels/xmleditor.html'}, name='xmleditor'),
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
