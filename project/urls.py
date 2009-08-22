from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings


admin.autodiscover()


urlpatterns = patterns('',
    # Explorer:
    url(r'^$', 'explorer.views.file_list', name='file_list'),
    url(r'^file/(?P<path>[^/]+)/$', 'explorer.views.file_xml', name='file_xml'),
    url(r'^images/(?P<folder>[^/]+)/$', 'explorer.views.folder_images', name='folder_image'),
    url(r'^images/$', 'explorer.views.folder_images', {'folder': '.'}, name='folder_image_ajax'),
    
    # Editor panels
    url(r'^editor/(?P<path>[^/]+)/panels/xmleditor/$', 'explorer.views.xmleditor_panel', name='xmleditor_panel'),
    url(r'^editor/(?P<path>[^/]+)/panels/gallery/$', 'explorer.views.gallery_panel', name='gallery_panel'),
    url(r'^editor/(?P<path>[^/]+)/panels/htmleditor/$', 'explorer.views.htmleditor_panel', name='htmleditor_panel'),
    
    # Admin panel
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/(.*)', admin.site.root),

    # Authorization
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'redirect_field_name': 'next_page'}),
    url(r'^accounts/logout$', 'django.contrib.auth.views.logout', {'next_page': '/'}), # {'redirect_field_name': 'next_page'}),
)


# Static files
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^%s(?P<path>.+)$' % settings.MEDIA_URL[1:], 'django.views.static.serve', 
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        url(r'^%s(?P<path>.+)$' % settings.STATIC_URL[1:], 'django.views.static.serve',
            {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
    )
