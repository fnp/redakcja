import json
import sys
from django.core.management import BaseCommand
from slugify import slugify
import wikidata
from catalogue.models import Book, Author


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('path')

    def handle(self, path, **kwargs):
        with open(path) as f:
            data = json.load(f)
        for item in data:
            if item['model'] == 'pdcounter.bookstub':
                continue
                notes = []
                slug = item['fields']['slug']
                book, created = Book.objects.get_or_create(slug=slug)
                if item['fields']['translator'] and not book.translators.exists():
                    notes.append('tłum.: ' + item['fields']['translator'])
                book.title = book.title or item['fields']['title']
                book.pd_year = book.pd_year or item['fields']['pd']
                notes = '\n'.join(notes)
                if notes and notes not in book.notes:
                    book.notes = '\n'.join([notes, book.notes])
                book.save()

                if not book.authors.exists():
                    author_name = item['fields']['author']
                    name_pieces = author_name.rsplit(' ', 1)
                    if len(name_pieces) == 1:
                        first_name, last_name = name_pieces, ''
                    else:
                        first_name, last_name = name_pieces

                    author, created = Author.objects.get_or_create(first_name=first_name, last_name=last_name)
                    if not author.slug:
                        print(author.slug, author_name)
                        author.slug = slugify(author_name)
                        author.save()
                    book.authors.set([author])
            elif item['model'] == 'pdcounter.author':
                slug = item['fields']['slug']
                author, created = Author.objects.get_or_create(slug=slug)
                if not author.first_name and not author.last_name:
                    author_name = item['fields']['name']
                    name_pieces = author_name.rsplit(' ', 1)
                    if len(name_pieces) == 1:
                        author.first_name, author.last_name = name_pieces, ''
                    else:
                        author.first_name, author.last_name = name_pieces
                    author.year_of_death = author.year_of_death or item['fields']['death']
                    author.notes = author.notes or item['fields']['description']
                    author.gazeta_link = author.gazeta_link or item['fields']['gazeta_link']
                    wiki_link = item['fields']['wiki_link']
                    assert not wiki_link # Welp
            else:
                print(item)
                break

