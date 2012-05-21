from os.path import abspath, dirname, join, basename, exists
from os import makedirs, listdir
from nose.tools import *
from mock import patch
from django.test import TestCase
from django.contrib.auth.models import User
from catalogue.models import Book, BookPublishRecord
from tempfile import mkdtemp
from django.conf import settings

def get_fixture(path):
    f_path = join(dirname(abspath(__file__)), 'files', path)
    with open(f_path) as f:
        return unicode(f.read(), 'utf-8')


class PublishTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='tester')
        self.text1 = get_fixture('chunk1.xml')
        self.book = Book.create(self.user, self.text1, slug='test-book')

    @patch('apiclient.api_call')
    def test_unpublishable(self, api_call):
        with self.assertRaises(AssertionError):
            self.book.publish(self.user)

    @patch('apiclient.api_call')
    def test_publish(self, api_call):
        self.book[0].head.set_publishable(True)
        self.book.publish(self.user)
        api_call.assert_called_with(self.user, 'books/', {"book_xml": self.text1})

    @patch('apiclient.api_call')
    def test_publish_multiple(self, api_call):
        self.book[0].head.set_publishable(True)
        self.book[0].split(slug='part-2')
        self.book[1].commit(get_fixture('chunk2.xml'))
        self.book[1].head.set_publishable(True)
        self.book.publish(self.user)
        api_call.assert_called_with(self.user, 'books/', {"book_xml": get_fixture('expected.xml')})


class ManipulationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='tester')
        self.book1 = Book.create(self.user, 'book 1', slug='book1')
        self.book2 = Book.create(self.user, 'book 2', slug='book2')

    def test_append(self):
        self.book1.append(self.book2)
        self.assertEqual(Book.objects.all().count(), 1)
        self.assertEqual(len(self.book1), 2)

    def test_append_to_self(self):
        with self.assertRaises(AssertionError):
            self.book1.append(Book.objects.get(pk=self.book1.pk))
        self.assertEqual(Book.objects.all().count(), 2)
        self.assertEqual(len(self.book1), 1)

    def test_prepend_history(self):
        self.book1.prepend_history(self.book2)
        self.assertEqual(Book.objects.all().count(), 1)
        self.assertEqual(len(self.book1), 1)
        self.assertEqual(self.book1.materialize(), 'book 1')

    def test_prepend_history_to_self(self):
        with self.assertRaises(AssertionError):
            self.book1.prepend_history(self.book1)
        self.assertEqual(Book.objects.all().count(), 2)
        self.assertEqual(self.book1.materialize(), 'book 1')
        self.assertEqual(self.book2.materialize(), 'book 2')

    def test_split_book(self):
        self.book1.chunk_set.create(number=2, title='Second chunk',
                slug='book3')
        self.book1[1].commit('I survived!')
        self.assertEqual(len(self.book1), 2)
        self.book1.split()
        self.assertEqual(set([b.slug for b in Book.objects.all()]),
                set(['book2', '1', 'book3']))
        self.assertEqual(
                Book.objects.get(slug='book3').materialize(),
                'I survived!')


class GalleryAppendTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='tester')
        self.book1 = Book.create(self.user, 'book 1', slug='book1')
        self.book1.chunk_set.create(number=2, title='Second chunk',
                slug='book 1 / 2')
        c=self.book1[0]
        c.gallery_start=0
        c=self.book1[1]
        c.gallery_start=2
        
        self.scandir = join(settings.MEDIA_ROOT, settings.IMAGE_DIR)
        if not exists(self.scandir):
            makedirs(self.scandir)

    def make_gallery(self, book, files):
        d = mkdtemp('gallery', dir=self.scandir)
        for named, cont in files.items():
            f = open(join(d, named), 'w')
            f.write(cont)
            f.close()
        book.gallery = basename(d)


    def test_both_indexed(self):
        self.book2 = Book.create(self.user, 'book 2', slug='book2')
        self.book2.chunk_set.create(number=2, title='Second chunk of second book',
                slug='book 2 / 2')
        c = self.book2[0]
        c.gallery_start = 0
        c = self.book2[1]
        c.gallery_start = 2

        self.make_gallery(self.book1, {
            '1-0001_1l' : 'aa',
            '1-0001_2r' : 'bb',
            '1-0002_1l' : 'cc',
            '1-0002_2r' : 'dd',
            })

        self.make_gallery(self.book2, {
            '1-0001_1l' : 'dd', # the same, should not be moved
            '1-0001_2r' : 'ff',
            '2-0002_1l' : 'gg',
            '2-0002_2r' : 'hh',
            })

        self.book1.append(self.book2)

        files = listdir(join(self.scandir, self.book1.gallery))
        self.assertEqual(files, [
            '1-0001_1l',
            '1-0001_2r',
            '1-0002_1l',
            '1-0002_2r',
            #            '2-0001_1l',
            '2-0001_2r',
            '3-0002_1l',
            '3-0002_2r',
            ])        

        self.assertEqual((3, 5), (self.book1[2].gallery_start, self.book1[3].gallery_start))
        
        
    def test_none_indexed(self):
        self.book2 = Book.create(self.user, 'book 2', slug='book2')
        self.make_gallery(self.book1, {
            '0001_1l' : 'aa',
            '0001_2r' : 'bb',
            '0002_1l' : 'cc',
            '0002_2r' : 'dd',
            })

        self.make_gallery(self.book2, {
            '0001_1l' : 'ee',
            '0001_2r' : 'ff',
            '0002_1l' : 'gg',
            '0002_2r' : 'hh',
            })

        self.book1.append(self.book2)

        files = listdir(join(self.scandir, self.book1.gallery))
        print files
        self.assertEqual(files, [
            '0-0001_1l',
            '0-0001_2r',
            '0-0002_1l',
            '0-0002_2r',
            '1-0001_1l',
            '1-0001_2r',
            '1-0002_1l',
            '1-0002_2r',
            ])        


    def test_none_indexed(self):
        import nose.tools
        self.book2 = Book.create(self.user, 'book 2', slug='book2')
        self.make_gallery(self.book1, {
            '1-0001_1l' : 'aa',
            '1-0001_2r' : 'bb',
            '1002_1l' : 'cc',
            '1002_2r' : 'dd',
            })

        self.make_gallery(self.book2, {
            '0001_1l' : 'ee',
            '0001_2r' : 'ff',
            '0002_1l' : 'gg',
            '0002_2r' : 'hh',
            })

        self.book1.append(self.book2)

        files = listdir(join(self.scandir, self.book1.gallery))
        print files
        self.assertEqual(files, [
            '0-1-0001_1l',
            '0-1-0001_2r',
            '0-1002_1l',
            '0-1002_2r',
            '1-0001_1l',
            '1-0001_2r',
            '1-0002_1l',
            '1-0002_2r',
            ])        
