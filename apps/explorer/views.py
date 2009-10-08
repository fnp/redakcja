# -*- coding: utf-8 -*-
import urllib2
import hg, re
from datetime import date

import librarian

from librarian import html, parser, dcparser
from librarian import ParseError, ValidationError

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.utils import simplejson as json
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required

from explorer import forms, models
from toolbar import models as toolbar_models

from django.forms.util import ErrorList

import wlrepo

#
# Some useful decorators

def file_branch(fileid, user=None):
    parts = fileid.split('$')
    return ('personal_'+ user.username + '_' if user is not None else '') \
        + 'file_' + parts[0]

def file_path(fileid):
    return 'pub_'+fileid+'.xml'

def with_repo(view):
    """Open a repository for this view"""
    def view_with_repo(request, *args, **kwargs):          
        kwargs['repo'] = wlrepo.open_library(settings.REPOSITORY_PATH, 'hg')
        return view(request, *args, **kwargs)
    return view_with_repo

#
def ajax_login_required(view):
    """Similar ro @login_required, but instead of redirect, 
    just return some JSON stuff with error."""
    def view_with_auth(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view(request, *args, **kwargs)
        # not authenticated
        return HttpResponse( json.dumps({'result': 'access_denied', 'errors': ['Brak dostępu.']}) );
    return view_with_auth

@login_required
# @with_repo
def display_editor(request, path):
    # this is the only entry point where we create an autobranch for the user
    # if it doesn't exists. All other views SHOULD fail.
    #def ensure_branch_exists():
    #    parent = repo.get_branch_tip('default')
    #    repo._create_branch(file_branch(path, request.user), parent)

#    try:
    #    repo.with_wlock(ensure_branch_exists)

    return direct_to_template(request, 'explorer/editor.html', extra_context={
        'fileid': path,
        'panel_list': ['lewy', 'prawy'],
        'availble_panels': models.EditorPanel.objects.all(),
        # 'scriptlets': toolbar_models.Scriptlet.objects.all()
    })
    
#
# View all files
#
@with_repo
def file_list(request, repo):   
    import api.forms
    from api.resources import library_resource

    bookform = api.forms.DocumentUploadForm()

    # short-circut the api document list
    doctree = library_resource.handler.read(request)
    # print "DOCTREE:", doctree['documents']
        
    return direct_to_template(request, 'explorer/file_list.html', extra_context={
        'filetree': doctree['documents'], 'bookform': bookform,
    })

@permission_required('explorer.can_add_files')
@with_repo
def file_upload(request, repo):
    from api.resources import library_resource
    from api.forms import DocumentUploadForm
    from django.http import HttpRequest, HttpResponseRedirect

    response = library_resource.handler.create(request)

    if isinstance(response, HttpResponse):
        data = json.loads(response.content)
        
        if response.status_code == 201:
            return HttpResponseRedirect( \
                reverse("editor_view", args=[ data['name'] ]) )
        else:
            bookform = DocumentUploadForm(request.POST, request.FILES)
            bookform.is_valid()
            
            return direct_to_template(request, 'explorer/file_upload.html',
                extra_context={'bookform': bookform } )
          

@login_required
def print_html(request, **kwargs):
    from api.resources import document_html_resource

    kwargs['stylesheet'] = 'legacy'
    
    output = document_html_resource.handler.read(request, **kwargs)

    if isinstance(output, HttpResponse):
        # errors = json.loads(output.content)
        output.mimetype = "text/plain"
        return output
    
    return direct_to_template(request, 'html4print.html',
        extra_context={'output': output, 'docid': kwargs['docid']},
        mimetype="text/html" )


def _add_references(message, issues):
    return message + " - " + ", ".join(map(lambda issue: "Refs #%d" % issue['id'], issues))

def _get_issues_for_file(fileid):
    uf = None
    try:
        uf = urllib2.urlopen(settings.REDMINE_URL + 'publications/issues/%s.json' % fileid)
        return json.loads(uf.read())
    except urllib2.HTTPError:
        return []
    finally:
        if uf: uf.close()

# =================
# = Pull requests =
# =================
def pull_requests(request):
    from explorer.models import PullRequest

    objects = PullRequest.objects.order_by('status')

    if not request.user.has_perm('explorer.book.can_share'):
        objects = objects.filter(comitter=request.user)

    
    return direct_to_template(request, 'manager/pull_request.html', 
        extra_context = {'objects': objects} )
