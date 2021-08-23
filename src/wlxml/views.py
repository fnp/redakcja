from io import BytesIO
from django.views.generic import TemplateView, ListView, DetailView
from . import models
from librarian.document import WLDocument
from librarian.builders import StandaloneHtmlBuilder


class XslView(TemplateView):
    template_name = 'wlxml/wl2html.xsl'
    content_type = 'application/xslt+xml'

    def get_context_data(self):
        ctx = super().get_context_data()
        tags = {}
        for t in models.Tag.objects.all():
            tags.setdefault(t.type, []).append(t.name)
        ctx['tags'] = tags
        return ctx


class EditorCSS(ListView):
    template_name = 'wlxml/editor.css'
    content_type = 'text/css'
    queryset = models.Tag.objects.all()
        

class TagsView(ListView):
    queryset = models.Tag.objects.all()


class TagView(DetailView):
    queryset = models.Tag.objects.all()
    slug_field = 'name'

