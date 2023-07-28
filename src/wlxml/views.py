from io import BytesIO
import json
from django.http import HttpResponse
from django.views.generic import TemplateView, ListView, DetailView, View
from . import models
from librarian.dcparser import BookInfo
from librarian.document import WLDocument
from librarian.builders import StandaloneHtmlBuilder
from librarian.meta.types.wluri import WLURI
from librarian.meta.types.text import LegimiCategory, Epoch, Kind, Genre, Audience, ThemaCategory, MainThemaCategory
from depot.legimi import legimi


class XslView(TemplateView):
    template_name = 'wlxml/wl2html.xsl'
    content_type = 'application/xslt+xml'

    def get_context_data(self):
        ctx = super().get_context_data()
        tags = {}
        for t in models.Tag.objects.all():
            tags.setdefault(t.type, []).append(t.name)
        ctx['tags'] = tags
        ctx['namespaces'] = {
	    "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
	    "http://purl.org/dc/elements/1.1/": "dc",
	    "http://www.w3.org/XML/1998/namespace": "xml",
            "": "wl",
        }
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


VALUE_TYPES = {
    LegimiCategory: {
        'widget': 'select',
        'options': [''] + list(legimi.CATEGORIES.keys()),
    },
    Audience: {
        'autocomplete': {
            'source': '/catalogue/terms/audience/',
        }
    },
    ThemaCategory: {
        'autocomplete': {
            'source': '/catalogue/terms/thema/',
        }
    },
    MainThemaCategory: {
        'autocomplete': {
            'source': '/catalogue/terms/thema-main/',
        }
    },
    Epoch: {
        'autocomplete': {
            'source': '/catalogue/terms/epoch/',
        }
    },
    Kind: {
        'autocomplete': {
            'source': '/catalogue/terms/kind/',
        }
    },
    Genre: {
        'autocomplete': {
            'source': '/catalogue/terms/genre/',
        }
    },
    WLURI: {
        "autocomplete": {
            "source": "/catalogue/terms/wluri/",
        }
    },
    "authors": {
        "autocomplete": {
            "source": "/catalogue/terms/author/",
        }
    },
    "translators": {
        "autocomplete": {
            "source": "/catalogue/terms/author/",
        }
    },
    "editors": {
        "autocomplete": {
            "source": "/catalogue/terms/editor/",
        }
    },
    "technical_editors": {
        "autocomplete": {
            "source": "/catalogue/terms/editor/",
        }
    },
    "type": {
        "autocomplete": {
            "source": ["text"]
        }
    },
    "title": {
        "autocomplete": {
            "source": "/catalogue/terms/book_title/",
        }
    },

    "language": {
        'widget': 'select',
        'options': [
            '',
            'pol',
            'eng',
            'fre',
            'ger',
            'lit',
        ],
    },
    "publisher": {
        "autocomplete": {
            "source": ["Fundacja Wolne Lektury"]
        }
    },

}



class MetaTagsView(View):
    def get(self, request):
        fields = []
        for f in BookInfo.FIELDS:
            d = {
                'name': f.name,
                'required': f.required,
                'multiple': f.multiple,
                'uri': f.uri,
                'value_type': {
                    'hasLanguage': f.value_type.has_language,
                    'name': f.value_type.__name__,
                }
            }
            d['value_type'].update(
                VALUE_TYPES.get(
                    f.value_type,
                    VALUE_TYPES.get(
                        f.name,
                        {}
                    )
                )
            )
            fields.append(d)

        return HttpResponse(
            'let META_FIELDS = ' + json.dumps(fields),
            content_type='text/javascript')
    
