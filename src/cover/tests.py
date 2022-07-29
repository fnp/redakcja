# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import re
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from unittest import skipUnless
from unittest.mock import patch
from documents.models import Book
from cover.forms import ImportForm
from cover.models import Image


IMAGE_PATH = __file__.rsplit('/', 1)[0] + '/tests/angelus-novus.jpeg'

with open(__file__.rsplit('/', 1)[0] + '/tests/book.xml') as f:
    SAMPLE_XML = f.read()


@skipUnless(settings.TEST_INTEGRATION, 'Skip integration tests')
class FlickrTests(TestCase):
    def assertEqualWithRe(self, dict1, dict2):
        self.assertEqual(len(dict1), len(dict2))
        for k, v in dict2.items():
            if isinstance(v, re.Pattern):
                self.assertRegex(dict1[k], v)
            else:
                self.assertEqual(dict1[k], v)

    def test_flickr(self):
        form = ImportForm({
            "source_url": "https://www.flickr.com/photos/rczajka/6941928577/in/photostream"
        })
        self.assertTrue(form.is_valid())
        self.assertEqualWithRe(
            form.cleaned_data,
            {
                'source_url': "https://www.flickr.com/photos/rczajka/6941928577/",
                'author': "Radek Czajka@Flickr",
                'title': "Pirate Stańczyk",
                'license_name': "CC BY 2.0",
                'license_url': "https://creativecommons.org/licenses/by/2.0/",
                'download_url': re.compile(r'\.staticflickr\.com'),
            }
        )

    def test_wikimedia_fal(self):
        form = ImportForm({
            "source_url": "https://commons.wikimedia.org/wiki/File:Valdai_IverskyMon_asv2018_img47.jpg"
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data,
            {
                'title': 'Valdai IverskyMon asv2018 img47',
                'author': 'A.Savin',
                'source_url': 'https://commons.wikimedia.org/wiki/File:Valdai_IverskyMon_asv2018_img47.jpg',
                'download_url': 'https://upload.wikimedia.org/wikipedia/commons/4/43/Valdai_IverskyMon_asv2018_img47.jpg',
                'license_url': 'http://artlibre.org/licence/lal/en',
                'license_name': 'FAL'
            }
        )

    def test_wikimedia_public_domain(self):
        form = ImportForm({
            "source_url": 'https://commons.wikimedia.org/wiki/File:Pymonenko_A_boy_in_a_straw_hat.jpg'
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data,
            {
                'title': 'Chłopiec w słomkowym kapeluszu',
                'author': 'Mykola Pymonenko',
                'source_url': 'https://commons.wikimedia.org/wiki/File:Pymonenko_A_boy_in_a_straw_hat.jpg',
                'download_url': 'https://upload.wikimedia.org/wikipedia/commons/9/9b/Pymonenko_A_boy_in_a_straw_hat.jpg',
                'license_url': 'https://pl.wikipedia.org/wiki/Domena_publiczna',
                'license_name': 'domena publiczna'
            }
        )
        
    def test_mnw(self):
        form = ImportForm({
            "source_url": 'https://cyfrowe.mnw.art.pl/pl/katalog/511078'
        })
        self.assertTrue(form.is_valid())
        self.assertEqualWithRe(
            form.cleaned_data,
            {
                'title': 'Chłopka (Baba ukraińska)',
                'author': 'Krzyżanowski, Konrad (1872-1922)',
                'source_url': 'https://cyfrowe.mnw.art.pl/pl/katalog/511078',
                'download_url': re.compile(r'https://cyfrowe-cdn\.mnw\.art\.pl/.*\.jpg'),
                'license_url': 'https://pl.wikipedia.org/wiki/Domena_publiczna',
                'license_name': 'domena publiczna'
            }
        )

    def test_quick_import(self):
        user = User.objects.create(username='test', is_superuser=True)
        self.client.force_login(user)

        book = Book.create(slug='test', text=SAMPLE_XML, creator=user)
        
        self.client.post(
            '/cover/quick-import/1/',
            {
                'url': 'https://cyfrowe.mnw.art.pl/pl/katalog/511078'
            }
        )

        self.assertEqual(Image.objects.all().count(), 1)
        self.assertEqual(book[0].history().count(), 2)
        self.assertIn(
            '<dc:relation.coverImage.attribution>Chłopka (Baba ukraińska), Krzyżanowski, Konrad (1872-1922), domena publiczna</dc:relation.coverImage.attribution>',
            book.materialize()
        )


class CoverPreviewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.book = Book.create(slug='test', text='<utwor/>', creator=None)

    def test_preview_from_bad_xml(self):
        response = self.client.post('/cover/preview/', data={"xml": ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'/media/static/img/sample_cover.png')

    @patch('cover.views.make_cover')
    def test_preview_from_minimal_xml(self, make_cover):
        response = self.client.post('/cover/preview/', data={"xml": SAMPLE_XML})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'/media/dynamic/cover/preview/', response.content)

    def test_bad_book(self):
        response = self.client.get('/cover/preview/test/')
        self.assertEqual(response.status_code, 302)

    @patch('cover.views.make_cover')
    def test_good_book(self, make_cover):
        self.book[0].commit(text=SAMPLE_XML)

        response = self.client.get('/cover/preview/test/1/3/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/cover/preview/test/1/')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Content-Disposition', response)

        response = self.client.get('/cover/preview/test/1/2/?download&width=100')
        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment', response['Content-Disposition'])


class TestAddCover(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='test', is_superuser=True)

    def test_add_image(self):
        self.client.force_login(self.user)

        response = self.client.get('/cover/add_image/')
        self.assertEqual(response.status_code, 200)
        
        with open(IMAGE_PATH, 'rb') as image_file:
            response = self.client.post(
                '/cover/add_image/',
                data={
                    'title': 'Angelus Novus',
                    'author': 'Paul Klee',
                    'license_name': 'domena publiczna',
                    'license_url': '',
                    'file': image_file,
                }
            )
        self.assertEqual(Image.objects.all().count(), 1)

class TestCover(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='test', is_superuser=True)
        with open(IMAGE_PATH, 'rb') as f:
            cls.img = Image.objects.create(
                title='Angelus Novus',
                author='Paul Klee',
                license_name='domena publiczna',
                license_url='',
                file=SimpleUploadedFile(
                    'angelus-novus.jpg',
                    f.read(),
                    content_type='image/jpeg'
                )
            )

    def test_image_list(self):
        response = self.client.get('/cover/image/')
        self.assertEqual(len(response.context['object_list']), 1)
        
    def test_image(self):
        response = self.client.get('/cover/image/1/')
        self.assertEqual(response.context['object'].title, 'Angelus Novus')

    def test_edit_image(self):
        self.client.force_login(self.user)
        response = self.client.post('/cover/image/1/', {
            'author': 'author',
            'title': 'changed title',
            'license_name': 'domena',
            'cut_top': 1,
            'cut_bottom': 1,
            'cut_left': 1,
            'cut_right': 1,
        })

        response = self.client.get('/cover/image/1/')
        self.assertEqual(response.context['object'].title, 'changed title')
        
        
    def test_image_file(self):
        response = self.client.get('/cover/image/1/file/')
        self.assertRegex(response['Location'], r'^/media/dynamic/cover/image/')
