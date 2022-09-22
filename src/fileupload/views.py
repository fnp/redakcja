# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import json
import os
from urllib.parse import quote
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_headers
from django.views.generic import FormView, View
from .forms import UploadForm


# Use sorl.thumbnail if available.
try:
    from sorl.thumbnail import default
except ImportError:
    def thumbnail(relpath):
        return settings.MEDIA_URL + relpath
else:
    def thumbnail(relpath):
        try:
            return default.backend.get_thumbnail(relpath, "x50").url
        except (IOError, ValueError):
            # That's not an image. No thumb.
            return None


class JSONResponse(HttpResponse):
    """JSON response class."""
    def __init__(self, obj='', mimetype="application/json", *args, **kwargs):
        content = json.dumps(obj)
        super(JSONResponse, self).__init__(content, mimetype, *args, **kwargs)


class UploadView(FormView):
    template_name = "fileupload/picture_form.html"
    form_class = UploadForm

    def get_object(self, request, *args, **kwargs):
        """Get any data for later use."""
        return None

    def get_directory(self):
        """Directory relative to MEDIA_ROOT. Must end with a slash."""
        return self.kwargs['path']

    def breadcrumbs(self):
        """List of tuples (name, url) or just (name,) for breadcrumbs.

        Probably only the last item (representing currently browsed dir)
        should lack url.

        """
        directory = self.get_directory()
        now_path = os.path.dirname(self.request.get_full_path())
        directory = os.path.dirname(directory)
        if directory:
            crumbs = [
                (os.path.basename(directory),)
            ]
            directory = os.path.dirname(directory)
            now_path = (os.path.dirname(now_path))
            while directory:
                crumbs.insert(0, (os.path.basename(directory), now_path+'/'))
                directory = os.path.dirname(directory)
                now_path = os.path.dirname(now_path)
            crumbs.insert(0, ('media', now_path))
        else:
            crumbs = [('media',)]
        return crumbs

    def get_safe_path(self, filename=""):
        """Finds absolute filesystem path of the browsed dir of file.
        
        Makes sure it's inside MEDIA_ROOT.
        
        """
        path = os.path.abspath(os.path.join(
                settings.MEDIA_ROOT,
                self.get_directory(),
                filename))
        if not path.startswith(settings.MEDIA_ROOT):
            raise Http404
        if filename:
            if not path.startswith(self.get_safe_path()):
                raise Http404
        return path

    def get_url(self, filename):
        """Finds URL of a file in browsed dir."""
        return settings.MEDIA_URL + self.get_directory() + quote(filename.encode('utf-8'))

    @method_decorator(vary_on_headers('Accept'))
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object(request, *args, **kwargs)
        return super(UploadView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            files = []
            path = self.get_safe_path()
            if os.path.isdir(path):
                for f in sorted(os.listdir(path)):
                    file_info = {
                        "name": f,
                    }
                    if os.path.isdir(os.path.join(path, f)):
                        file_info.update({
                            "url": "%s%s/" % (request.get_full_path(), f),
                        })
                    else:
                        file_info.update({
                            "url": self.get_url(f),
                            'thumbnail_url': thumbnail(self.get_directory() + f),
                            'delete_url': "%s?file=%s" % (
                                request.get_full_path(),
                                quote(f.encode('utf-8'))),
                            'delete_type': "DELETE"
                        })
                        thumbnail_url = thumbnail(self.get_directory() + f),
                    files.append(file_info)
            return JSONResponse(files)
        else:
            return super(UploadView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        flist = self.request.FILES.getlist('files')
        path = self.get_safe_path()
        if not os.path.isdir(path):
            os.makedirs(path)
        data = []
        for f in flist:
            with open(self.get_safe_path(f.name), 'wb') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            data.append({
                'name': f.name, 
                'url': self.get_url(f.name),
                'thumbnail_url': thumbnail(self.get_directory() + f.name),
                        'delete_url': "%s?file=%s" % (
                            self.request.get_full_path(),
                            quote(f.name.encode('utf-8'))),
                'delete_type': "DELETE"
            })
        response = JSONResponse(data)
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

    def delete(self, request, *args, **kwargs):
        os.unlink(self.get_safe_path(request.GET.get('file')))
        response = JSONResponse(True)
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
