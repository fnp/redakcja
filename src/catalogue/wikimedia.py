from urllib.parse import unquote
from django.core.files.base import ContentFile
from cover.utils import get_wikimedia_data, URLOpener


class WikiMedia:
    def get_description_url(imgdata):
        if imgdata is None:
            return None
        return imgdata.attributes['imageinfo'][0]['descriptionurl']

    @classmethod
    def descriptionurl(cls, arg):
        def transform(get_value):
            value = get_value(arg)
            if value is None:
                return None
            return cls.get_description_url(value)
        return transform

    @classmethod
    def attribution(cls, arg):
        def transform(get_value):
            value = get_value(arg)
            if value is None:
                return None
            media_data = get_wikimedia_data(
                cls.get_description_url(value)
            )
            parts = [
                media_data['title'],
                media_data['author'],
                media_data['license_name'],
            ]
            parts = [p for p in parts if p]
            attribution = ', '.join(parts)
            return attribution
        return transform

    @classmethod
    def download(cls, arg):
        def transform(get_value):
            value = get_value(arg)
            if value is None:
                return None
            media_data = get_wikimedia_data(
                cls.get_description_url(value)
            )
            download_url = media_data['download_url']
            return Downloadable(download_url)
        return transform

    @classmethod
    def append(cls, arg):
        def transform(get_value):
            value = get_value(arg)
            return Appendable(value)
        return transform


class Appendable(str):
    def as_hint_json(self):
        return {
            'value': self,
            'action': 'append',
        }
    
class Downloadable:
    def __init__(self, url):
        self.url = url

    def apply_to_field(self, obj, attname):
        t = URLOpener().open(self.url).read()
        getattr(obj, attname).save(
            unquote(self.url.rsplit('/', 1)[-1]),
            ContentFile(t),
            save=False
        )

    def as_hint_json(self):
        return {
            'download': self.url,
            'img': self.url,
        }
