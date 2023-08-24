from datetime import date
import io
import json
import re
from time import sleep
from django.conf import settings
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from librarian.builders.html import SnippetHtmlBuilder
from librarian.functions import lang_code_3to2
from catalogue.models import Audience, Author, Thema
from .. import models
from .base import BasePublisher
from .woblink_constants import WOBLINK_CATEGORIES


class WoblinkError(ValueError):
    pass

class NoPrice(WoblinkError):
    def as_html(self):
        return format_html(
            'Brak <a href="/admin/depot/shop/{price}">określonej ceny</a>.',
            price=self.args[0].id
        )

class NoIsbn(WoblinkError):
    def as_html(self):
        return 'Brak ISBN.'

class AuthorLiteralForeign(WoblinkError):
    def as_html(self):
        return format_html(
            'Nie obsługiwane: autor „{author}” w języku {lang}.',
            author=str(self.args[0]),
            lang=self.args[0].lang,
        )

class AuthorNotInCatalogue(WoblinkError):
    def as_html(self):
        return format_html(
            'Brak autora „{author}” w katalogu.',
            author=str(self.args[0])
        )

class AuthorNoWoblink(WoblinkError):
    def as_html(self):
        return format_html(
            'Autor <a href="/admin/catalogue/author/{author_id}/">{author}</a> bez identyfikatora Woblink.',
            author_id=self.args[0].id,
            author=self.args[0].name
        )

class NoThema(WoblinkError):
    def as_html(self):
        return format_html('Brak Thema.')

class UnknownThema(WoblinkError):
    def as_html(self):
        return format_html(
            'Nieznana Thema {code}.',
            code=self.args[0]
        )


class ThemaUnknownWoblink(WoblinkError):
    def as_html(self):
        return format_html(
            'Thema <a href="/admin/catalogue/thema/{id}/">{code}</a> przypisana do nieznanej kategorii Woblink.',
            id=self.args[0].id,
            code=self.args[0].code,
        )

class NoWoblinkCategory(WoblinkError):
    def as_html(self):
        return 'Brak kategorii Woblink.'

class WoblinkWarning(Warning):
    pass

class NoMainThemaWarning(WoblinkWarning):
    def as_html(self):
        return format_html(
            'Brak głównej kategorii Thema.'
        )

class ThemaNoWoblink(WoblinkWarning):
    def as_html(self):
        return format_html(
            'Thema <a href="/admin/catalogue/thema/{id}/">{code}</a> nie przypisana do kategorii Woblink.',
            id=self.args[0].id,
            code=self.args[0].code,
        )

class AuthorLiteralForeignWarning(WoblinkWarning):
    def as_html(self):
        return format_html(
            'Nie obsługiwane: autor „{author}” w języku {lang}.',
            author=str(self.args[0]),
            lang=self.args[0].lang,
        )

class AuthorNotInCatalogueWarning(WoblinkWarning):
    def as_html(self):
        return format_html(
            'Brak autora „{author}” w katalogu.',
            author=str(self.args[0])
        )

class AuthorNoWoblinkWarning(WoblinkWarning):
    def as_html(self):
        return format_html(
            'Autor <a href="/admin/catalogue/author/{author_id}/">{author}</a> bez identyfikatora Woblink.',
            author_id=self.args[0].id,
            author=self.args[0].name
        )




class Woblink(BasePublisher):
    BASE_URL = 'https://publisher.woblink.com/'
    ADD_URL = BASE_URL + 'catalog/add'
    STEP1_URL = BASE_URL + 'catalog/edit/%s'
    STEP2_URL = BASE_URL + 'catalog/edit/%s/2'
    STEP3_URL = BASE_URL + 'catalog/edit/%s/3'
    STEP4_URL = BASE_URL + 'catalog/edit/%s/4'
    STEP5_URL = BASE_URL + 'catalog/edit/%s/5'
    UPLOAD_URL = BASE_URL + 'file/upload-%s'
    JOB_STATUS_URL = BASE_URL + 'task/status'
    GENERATE_DEMO_URL = BASE_URL + 'task/run/generate-%s-demo/%s/%d'
    CHECK_DEMO_URL = BASE_URL + 'task/run/check-%s-demo/%s'

    SEARCH_CATALOGUE_URL = BASE_URL + '{category}/autocomplete/{term}'

    ROLE_AUTHOR = 1
    ROLE_TRANSLATOR = 4

    def login(self):
        response = self.session.get('https://publisher.woblink.com/login')
        token = re.search(
            r'name="_csrf_token" value="([^"]+)"',
            response.text
        ).group(1)
        data = {
            '_csrf_token': token,
            '_username': self.username,
            '_password': self.password,
        }
        response = self.session.post(
            'https://publisher.woblink.com/login_check',
            data=data,
        )

    def search_catalogue(self, category, term):
        return self.session.get(
            self.SEARCH_CATALOGUE_URL.format(category=category, term=term)
        ).json()

    def search_author_catalogue(self, term):
        return [
            {
                'id': item['autId'],
                'text': item['autFullname']
            }
            for item in self.search_catalogue('author', term)
        ]
    def search_series_catalogue(self, term):
        return [
            {
                'id': item['id'],
                'text': item['name']
            }
            for item in self.search_catalogue('series', term)
        ]
        
    def get_isbn(self, meta, errors=None):
        if not meta.isbn_epub:
            if errors is not None:
                errors.append(NoIsbn())
        return meta.isbn_epub

    def get_authors_data(self, meta, errors=None):
        authors = []
        for role, items, obligatory in [
                (self.ROLE_AUTHOR, meta.authors, True),
                (self.ROLE_TRANSLATOR, meta.translators, False)
        ]:
            for person_literal in items:
                if person_literal.lang != 'pl':
                    if errors is not None:
                        if obligatory:
                             errors.append(AuthorLiteralForeign(person_literal))
                        else:
                            errors.append(AuthorLiteralForeignWarning(person_literal))
                    continue
                aobj = Author.get_by_literal(str(person_literal))
                if aobj is None:
                    if errors is not None:
                        if obligatory:
                             errors.append(AuthorNotInCatalogue(person_literal))
                        else:
                            errors.append(AuthorNotInCatalogueWarning(person_literal))
                    continue
                if not aobj.woblink:
                    if errors is not None:
                        if obligatory:
                             errors.append(AuthorNoWoblink(aobj))
                        else:
                            errors.append(AuthorNoWoblinkWarning(aobj))
                    continue
                authors.append((role, aobj.woblink))
        return authors

    def get_genres(self, meta, errors=None):
        thema_codes = []
        if meta.thema_main:
            thema_codes.append(meta.thema_main)
        else:
            if errors is not None:
                errors.append(NoMainThemaWarning())
        thema_codes.extend(meta.thema)

        thema_codes.extend(
            Audience.objects.filter(code__in=meta.audiences).exclude(
                thema=None).values_list('thema', flat=True)
        )

        if not thema_codes:
            if errors is not None:
                errors.append(NoThema())
        category_ids = []
        for code in thema_codes:
            try:
                thema = Thema.objects.get(code=code)
            except Thema.DoesNotExist:
                if errors is not None:
                    errors.append(UnknownThema(code))
            else:
                if thema.woblink_category is None:
                    if errors is not None:
                        errors.append(ThemaNoWoblink(thema))
                elif thema.woblink_category not in WOBLINK_CATEGORIES:
                    if errors is not None:
                        errors.append(ThemaUnknownWoblink(thema))
                elif thema.woblink_category not in category_ids:
                    category_ids.append(thema.woblink_category)
        if not category_ids:
            if errors is not None:
                errors.append(NoWoblinkCategory())
        return category_ids

    def get_series(self, meta, errors=None):
        return list(Audience.objects.filter(code__in=meta.audiences).exclude(
            woblink=None).values_list('woblink', flat=True))

    def get_abstract(self, wldoc, errors=None, description_add=None):
        description = self.get_description(wldoc, description_add)
        parts = description.split('\n', 1)
        if len(parts) == 1 or len(parts[0]) > 240:
            # No newline found here.
            # Try to find last sentence end..
            parts = re.split(r' \.', description[240::-1], 1)
            if len(parts) == 2:
                p1 = parts[1][::-1] + '.'
                p2 = description[len(p1) + 1:]
            else:
                # No sentence end found.
                # Just find a space.
                p1 = description[:240].rsplit(' ', 1)[0]
                p2 = description[len(p1) + 1:]
                p1 += '…'
                p2 = '…' + p2
            parts = [p1, p2]

        m = re.search(r'<[^>]+$', parts[0])
        if m is not None:
            parts[0] = parts[0][:-len(m.group(0))]
            parts[1] = m.group(0) + parts[1]

        opened = []
        for tag in re.findall(r'<[^>]*[^/>]>', parts[0]):
            if tag[1] == '/':
                opened.pop()
            else:
                opened.append(tag)
        for tag in reversed(opened):
            parts[0] += '</' + tag[1:-1].split()[0] + '>'
            parts[1] = tag + parts[1]
        return {
            'header': parts[0],
            'rest': parts[1],
        }

    def get_lang2code(self, meta, errors=None):
        return lang_code_3to2(meta.language)

    def get_price(self, shop, wldoc, errors=None):
        try:
            stats = wldoc.get_statistics()['total']
        except:
            if errors:
                errors.append(NoPrice(shop))
            return 0
        words = stats['words_with_fn']
        pages = stats['chars_with_fn'] / 1800
        price = shop.get_price(words, pages)
        if price is None:
            if errors:
                errors.append(NoPrice(shop))
            return 0

        return price

    def can_publish(self, shop, book):
        wldoc = book.wldocument(librarian2=True)
        d = {
            'warnings': [],
            'errors': [],
            'info': [],
        }
        errors = []
        book_data = self.get_book_data(shop, wldoc, errors)
        for error in errors:
            if not isinstance(error, Warning):
                errlist = d['errors']
            else:
                errlist = d['warnings']
            errlist.append(error.as_html())

        if book_data.get('genres'):
            d['info'].append(format_html(
                'W kategoriach: {cat} ({price} zł)',
                cat=', '.join(self.describe_category(g) for g in book_data['genres']),
                price=book_data['price'],
            ))
        d['info'].append(mark_safe(
            '<strong>' + book_data['abstract']['header'] +
            '</strong><br/>' + book_data['abstract']['rest']
        ))

        return d

    def describe_category(self, category):
        t = []
        while category:
            c = WOBLINK_CATEGORIES[category]
            t.append(c['name'])
            category = c.get('parent')
        return ' / '.join(reversed(t))

    def create_book(self, isbn):
        isbn = ''.join(c for c in isbn if c.isdigit())
        assert len(isbn) == 13
        response = self.session.post(
            self.ADD_URL,
            data={
                'AddPublication[pubType]': 'ebook',
                'AddPublication[pubHasIsbn]': '1',
                'AddPublication[pubIsbn]': isbn,
                 ##AddPubation[save]
            }
        )
        m = re.search(r'/(\d+)$', response.url)
        if m is not None:
            return m.group(1)

    def send_book(self, shop, book, changes=None):
        wldoc = book.wldocument(librarian2=True, changes=changes, publishable=False) # TODO pub
        meta = wldoc.meta

        book_data = self.get_book_data(shop, wldoc)

        if not book.woblink_id:
            #book.woblink_id = 2959868
            woblink_id = self.create_book(book_data['isbn'])
            assert woblink_id
            book.woblink_id = woblink_id
            book.save(update_fields=['woblink_id'])

        self.edit_step1(book.woblink_id, book_data)
        self.edit_step2(book.woblink_id, book_data)
        self.edit_step3(book.woblink_id, book_data)
        cover_id = self.send_cover(book.woblink_id, wldoc)

        texts = shop.get_texts()
        epub_id, epub_demo = self.send_epub(
            book.woblink_id, wldoc, book.gallery_path(),
            fundraising=texts
        )
        mobi_id, mobi_demo = self.send_mobi(
            book.woblink_id, wldoc, book.gallery_path(),
            fundraising=texts
        )
        self.edit_step4(
            book.woblink_id, book_data,
            cover_id, epub_id, epub_demo, mobi_id, mobi_demo,
        )
        self.edit_step5(book.woblink_id, book_data)

    def get_book_data(self, shop, wldoc, errors=None):
        return {
            "title": wldoc.meta.title,
            "isbn": self.get_isbn(wldoc.meta, errors=errors),
            "authors": self.get_authors_data(wldoc.meta, errors=errors),
            "abstract": self.get_abstract(
                wldoc, errors=errors, description_add=shop.description_add
            ),
            "lang2code": self.get_lang2code(wldoc.meta, errors=errors),
            "genres": self.get_genres(wldoc.meta, errors=errors),
            "price": self.get_price(shop, wldoc, errors=errors),
            "series": self.get_series(wldoc.meta, errors=errors),
        }

    def with_form_name(self, data, name):
        return {
            f"{name}[{k}]": v
            for (k, v) in data.items()
        }

    def edit_step1(self, woblink_id, book_data):
        data = book_data

        authors_data = [
            {
                "AhpPubId": woblink_id,
                "AhpAutId": author_id,
                "AhpType": author_type,
            }
            for (author_type, author_id) in data['authors']
        ]

        series_data = [
            {
                'PublicationId': woblink_id,
                'SeriesId': series_id,
            }
            for series_id in data['series']
        ]

        d = {
            'pubTitle': book_data['title'],
            'npwAuthorHasPublications': json.dumps(authors_data),
            'pubShortNote': data['abstract']['header'],
            'pubNote': data['abstract']['rest'],
            'pubCulture': data['lang2code'],
            'npwPublicationHasAwards': '[]',
            'npwPublicationHasSeriess': json.dumps(series_data),
        }
        d = self.with_form_name(d, 'EditPublicationStep1')
        d['roles'] = [author_type for (author_type, author_id) in data['authors']]
        r = self.session.post(self.STEP1_URL % woblink_id, data=d)
        return r


    def edit_step2(self, woblink_id, book_data):
        gd = {}
        legacy = None
        for i, g in enumerate(book_data['genres']):
            gdata = WOBLINK_CATEGORIES[g]
            if legacy is None:
                legacy = gdata.get('legacy')
            if p := gdata.get('parent'):
                gd.setdefault(p, {'isMain': False})
                gd[p].setdefault('children', [])
                gd[p]['children'].append(str(g))
                gd[p].setdefault('mainChild', str(g))
                if legacy is None:
                    legacy = WOBLINK_CATEGORIES[p].get('legacy')
            else:
                gd.setdefault(g, {})
                gd[g]['isMain'] = True
        gd = [
            {
                "pubId": woblink_id,
                "category": str(k),
                **v
            }
            for k, v in gd.items()
        ]

        data = {
            'npwPublicationHasNewGenres': json.dumps(gd),
            'genre': legacy or '',
        }
        data = self.with_form_name(data, 'AddPublicationStep2')
        return self.session.post(self.STEP2_URL % woblink_id, data=data)

    def edit_step3(self, woblink_id, book_data):
        d = {
            'pubBasePrice': book_data['price'],
            'pubPremiereDate': date.today().isoformat(),
            'pubIsLicenseIndefinite': '1',
            'pubFileFormat': 'epub+mobi',
            'pubIsAcs': '0',
            'pubPublisherIndex': '',
            'save_and_continue': '',
        }
        d = self.with_form_name(d, 'EditPublicationStep3')
        return self.session.post(self.STEP3_URL % woblink_id, data=d)

    def edit_step4(self, woblink_id, book_data, cover_id, epub_id, epub_demo, mobi_id, mobi_demo):
        d = {
            'pubCoverResId': cover_id,
            'pubEpubResId': epub_id,
            'pubEpubDemoResId': epub_demo,
            'pubMobiResId': mobi_id,
            'pubMobiDemoResId': mobi_demo,
            'pubFileFormat': 'epub+mobi',
            'pubId': woblink_id,
            'save_and_continue': '',
        }
        d = self.with_form_name(d, 'EditPublicationStep4')
        return self.session.post(self.STEP4_URL % woblink_id, data=d)

    def edit_step5(self, woblink_id, book_data):
        d = {'save': ''}
        d = self.with_form_name(d, 'EditPublicationStep5')
        return self.session.post(self.STEP5_URL % woblink_id, data=d)

    def wait_for_job(self, job_id):
        while True:
            response = self.session.post(
                self.JOB_STATUS_URL,
                data={'ids[]': job_id}
            )
            data = response.json()[job_id]
            if data['ready']:
                assert data['successful']
                return data.get('returnValue')
            sleep(2)

    def upload_file(self, woblink_id, filename, content, field_name, mime_type):
        form_name = f'Upload{field_name}'
        id_field = f'pub{field_name}ResId'
        field_name = field_name.lower()

        data = {
            'pubId': woblink_id,
        }
        files = {
            field_name: (filename, content, mime_type)
        }
        
        response = self.session.post(
            self.UPLOAD_URL % field_name,
            data=self.with_form_name(data, form_name),
            files=self.with_form_name(files, form_name),
        )
        resp_data = response.json()
        assert resp_data['success'] is True
        file_id = resp_data[id_field]
        if 'jobId' in resp_data:
            self.wait_for_job(resp_data['jobId'])
        return file_id

    def generate_demo(self, woblink_id, file_format, check=True):
        percent = 10
        while True:
            job_id = self.session.get(
                self.GENERATE_DEMO_URL % (file_format, woblink_id, percent),
            ).json()['jobId']
            try:
                file_id = self.wait_for_job(job_id)
            except AssertionError:
                if percent < 50:
                    percent += 10
                else:
                    raise
            else:
                break

        if check:
            self.wait_for_job(
                self.session.get(
                    self.CHECK_DEMO_URL % (file_format, woblink_id)
                ).json()['jobId']
            )
        return file_id

    def send_epub(self, woblink_id, doc, gallery_path, fundraising=None):
        from librarian.builders import EpubBuilder
        content = EpubBuilder(
            base_url='file://' + gallery_path + '/',
            fundraising=fundraising or [],
        ).build(doc).get_file()
        file_id = self.upload_file(
            woblink_id,
            doc.meta.url.slug + '.epub',
            content,
            'Epub',
            'application/epub+zip'
        )
        demo_id = self.generate_demo(woblink_id, 'epub')
        return file_id, demo_id

    def send_mobi(self, woblink_id, doc, gallery_path, fundraising=None):
        from librarian.builders import MobiBuilder
        content = MobiBuilder(
            base_url='file://' + gallery_path + '/',
            fundraising=fundraising or [],
        ).build(doc).get_file()
        file_id = self.upload_file(
            woblink_id,
            doc.meta.url.slug + '.mobi',
            content,
            'Mobi',
            'application/x-mobipocket-ebook'
        )
        demo_id = self.generate_demo(woblink_id, 'mobi', check=False)
        return file_id, demo_id

    def send_cover(self, woblink_id, doc):
        from librarian.cover import make_cover
        # TODO Labe
        # A5 @ 300ppi.
        cover = make_cover(doc.meta, cover_class='m-label', width=1748, height=2480)
        content = io.BytesIO()
        cover.final_image().save(content, cover.format)
        content.seek(0)
        file_id = self.upload_file(
            woblink_id,
            doc.meta.url.slug + '.jpeg',
            content,
            'Cover',
            cover.mime_type()
        )
        return file_id
