import json
import os
from .forms import UploadForm
from django.views.generic import FormView, View
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.conf import settings


class JSONResponse(HttpResponse):
    """JSON response class."""
    def __init__(self, obj='', mimetype="application/json", *args, **kwargs):
        content = json.dumps(obj)
        super(JSONResponse, self).__init__(content, mimetype, *args, **kwargs)

class UploadView(FormView):
    template_name = "fileupload/picture_form.html"
    form_class = UploadForm

    def get_safe_path(self, filename=""):
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

    def get_url(self, filename=""):
        return settings.MEDIA_URL + self.get_directory() + filename

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object(request, *args, **kwargs)
        return super(UploadView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            files = []
            
            path = self.get_safe_path()
            if os.path.isdir(path):
                for f in os.listdir(path):
                    files.append({
                        "name": f,
                        "url": self.get_url(f),
                        'thumbnail_url': self.get_url(f), # FIXME: thumb!
                        'delete_url': "%s?file=%s" % (request.get_full_path(), f), # FIXME: encode
                        'delete_type': "DELETE"
                    })
            return JSONResponse(files)
        else:
            return super(UploadView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        f = self.request.FILES.get('file')
        path = self.get_safe_path()
        
        if not os.path.isdir(path):
            os.makedirs(path)
        with open(self.get_safe_path(f.name), 'w') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        data = [{
            'name': f.name, 
            'url': self.get_url(f.name),
            'thumbnail_url': self.get_url(f.name), # FIXME: thumb!
            'delete_url': "%s?file=%s" % (self.request.get_full_path(), f.name), # FIXME: encode
            'delete_type': "DELETE"
        }]
        response = JSONResponse(data)
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

    def delete(self, request, *args, **kwargs):
        os.unlink(self.get_safe_path(request.GET.get('file')))
        response = JSONResponse(True)
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
