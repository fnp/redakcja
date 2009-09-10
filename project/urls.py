from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()
PATH_SEC = r"(?P<path>[^/]+)"
PATH_END = PATH_SEC + "/$"

urlpatterns = patterns('',
    # Explorer:
    url(r'^$', 'explorer.views.file_list', name='file_list'),
    
    url(r'^file/'+PATH_SEC+'/text/$', 'explorer.views.file_xml', name='file_xml'),
    url(r'^file/'+PATH_SEC+'/dc/$', 'explorer.views.file_dc', name='file_dc'),
    url(r'^file/upload', 'explorer.views.file_upload', name='file_upload'),
    url(r'^file/'+PATH_SEC+'/commit$', 'explorer.views.file_commit', name='file_commit'),
    url(r'^file/'+PATH_SEC+'/update$', 'explorer.views.file_update_local', name='file_update'),

    url(r'^images/(?P<folder>[^/]+)/$', 'explorer.views.folder_images', name='folder_image'),
    url(r'^images/$', 'explorer.views.folder_images', {'folder': '.'}, name='folder_image_ajax'),
    
    # Editor panels
    url(r'^editor/'+PATH_SEC+'/panel/(?P<name>[a-z]+)/$', 'explorer.views.panel_view', name='panel_view'),
    url(r'^editor/'+PATH_END, 'explorer.views.display_editor', name='editor_view'),

    url(r'^editor/'+PATH_SEC+'/split$', 'explorer.views.split_text'),
    url(r'^editor/'+PATH_SEC+'/split-success',
        'explorer.views.split_success', name='split-success'),

    url(r'^editor/'+PATH_SEC+'/print/html$', 'explorer.views.print_html'),
    url(r'^editor/'+PATH_SEC+'/print/xml$', 'explorer.views.print_xml'),
    
    # Task managment
    url(r'^manager/pull-requests$', 'explorer.views.pull_requests'),

    # Admin panel
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/(.*)', admin.site.root),

    # Authorization
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'redirect_field_name': 'next'}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
)


# Static files
if settings.DEBUG and not hasattr(settings, 'DONT_SERVE_STATIC'):
    urlpatterns += patterns('',
        url(r'^%s(?P<path>.+)$' % settings.MEDIA_URL[1:], 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        url(r'^%s(?P<path>.+)$' % settings.STATIC_URL[1:], 'django.views.static.serve',
            {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
    )
