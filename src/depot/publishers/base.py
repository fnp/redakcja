import requests
from librarian.html import transform_abstrakt
from slugify import slugify


class BasePublisher:
    def __init__(self, username, password, publisher_handle):
        self.username = username
        self.password = password
        self.publisher_handle = publisher_handle
        self._session = None

    @property
    def session(self):
        if self._session is None:
            self._session = requests.Session()
            self.login()
        return self._session

    def send_book(self, site_book_publish, changes=None):
        raise NotImplementedError()

    def get_description(self, wlbook, description_add=''):
        description = ''

        if wlbook.meta.audience in ('L', 'SP1', 'SP2', 'SP3', 'SP4'):
            description += '<p><em>{}</em> to lektura szkolna.'.format(wlbook.meta.title)
            if wlbook.tree.find('//pe') is not None:
                description += '<br>Ebook <em>{title}</em> zawiera przypisy opracowane specjalnie dla uczennic i uczniów {school}.'.format(
                    title=wlbook.meta.title,
                    school='szkoły podstawowej' if wlbook.meta.audience.startswith('SP') else 'liceum i technikum'
                )
            description += '</p>\n'

        abstract = wlbook.tree.find('.//abstrakt')
        if abstract is not None:
            description += transform_abstrakt(abstract)
        description += description_add
        description += '<p>'
        description += ', '.join(
            '<a href="https://wolnelektury.pl/katalog/autor/{}/">{}</a>'.format(
                slugify(p.readable()),
                p.readable(),
            ) if p is not None else ''
            for p in wlbook.meta.authors
        ) + '<br>'
        description += '<a href="https://wolnelektury.pl/katalog/lektura/{}/">{}</a><br>'.format(
            wlbook.meta.url.slug,
            wlbook.meta.title
        )
        if wlbook.meta.translators:
            description += 'tłum. ' + ', '.join(p.readable() for p in wlbook.meta.translators) + '<br>'
        description += 'Epoka: ' + ', '.join(
            '<a href="https://wolnelektury.pl/katalog/epoka/{}/">{}</a>'.format(
                slugify(p),
                p,
            ) if p is not None else ''
            for p in wlbook.meta.epochs
        ) + ' '
        description += 'Rodzaj: ' + ', '.join(
            '<a href="https://wolnelektury.pl/katalog/rodzaj/{}/">{}</a>'.format(
                slugify(p),
                p,
            ) if p is not None else ''
            for p in wlbook.meta.kinds
        ) + ' '
        description += 'Gatunek: ' + ', '.join(
            '<a href="https://wolnelektury.pl/katalog/gatunek/{}/">{}</a>'.format(
                slugify(p),
                p,
            ) if p is not None else ''
            for p in wlbook.meta.genres
        ) + '</p>'

        return description

