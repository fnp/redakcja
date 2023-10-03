from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.views.generic import DetailView
from fileupload.views import UploadView
from . import models


# TODO 
class SourceView(DetailView):
    model = models.Source


class SourceUploadView(UploadView):
    def get_object(self, request, sid):
        source = get_object_or_404(models.Source, id=sid)
        return source

    def breadcrumbs(self):
        return [
            (_('sources'),),
            (self.object.name, self.object.get_absolute_url()),
            (_('upload'),)
        ]

    def get_directory(self):
        return self.object.get_upload_directory()

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.touch()
        return response

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        self.object.touch()
        return response


def prepare(request, bsid):
    bs = get_object_or_404(models.BookSource, id=bsid)

    if request.POST:
        dbook = bs.prepare_document(request.user)
        return redirect('wiki_editor', dbook.slug, dbook[0].slug)
    else:
        return render(
            request,
            'sources/prepare.html',
            {
                'book_source': bs,
            }
        )
