from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.views.generic import DetailView
from fileupload.views import UploadView
import catalogue.models
from . import models


# TODO 
class SourceView(DetailView):
    model = models.Source


class SourceUploadView(UploadView):
    template_name = 'sources/upload.html'

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


def prepare(request, pk):
    book = get_object_or_404(catalogue.models.Book, id=pk)

    if request.POST:
        dbook = models.BookSource.prepare_document(book, request.user)
        return redirect('wiki_editor', dbook.slug, dbook[0].slug)
    else:
        return redirect(book.get_absolute_url())
