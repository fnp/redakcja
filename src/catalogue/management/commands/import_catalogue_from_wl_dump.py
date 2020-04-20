# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import json
from urllib.request import urlopen
import sys
from django.core.management import BaseCommand
from slugify import slugify
import wikidata
from catalogue.models import Book, Author


def parse_name(name):
    name_pieces = name.rsplit(" ", 1)
    if len(name_pieces) == 1:
        return name_pieces[0], ""
    else:
        return name_pieces


def find_wikidata(link, lang):
    link = link.rstrip()
    title = link.rsplit("/", 1)[-1]
    title = title.split("#", 1)[0]
    title = title.replace(" ", "_")
    data = json.load(
        urlopen(
            f"https://www.wikidata.org/w/api.php?action=wbgetentities&sites={lang}wiki&titles={title}&format=json"
        )
    )
    wikidata_id = list(data["entities"].keys())[0]
    if not wikidata_id.startswith("Q"):
        return None
    return wikidata_id


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, path, **kwargs):
        with open(path) as f:
            data = json.load(f)

        for pass_n in (1, 2):
            for item in data:
                if item["model"] == "pdcounter.bookstub":
                    if pass_n != 2:
                        continue
                    notes = []
                    print(item["fields"]["author"], item["fields"]["title"])
                    slug = item["fields"]["slug"]
                    book, created = Book.objects.get_or_create(slug=slug)
                    if item["fields"]["translator"] and not book.translators.exists():
                        notes.append("tłum.: " + item["fields"]["translator"])
                    book.title = book.title or item["fields"]["title"]
                    book.pd_year = book.pd_year or item["fields"]["pd"]
                    notes = "\n".join(notes)
                    if notes and notes not in book.notes:
                        book.notes = "\n".join([notes, book.notes])
                    book.save()

                    if not book.authors.exists():
                        first_name, last_name = parse_name(item["fields"]["author"])
                        author_slug = slugify(item["fields"]["author"])
                        author = (
                            Author.objects.filter(slug=author_slug).first()
                            or Author.objects.filter(
                                first_name=first_name, last_name=last_name
                            ).first()
                            or Author()
                        )
                        author.slug = author.slug or author_slug
                        author.first_name = author.first_name or first_name
                        author.last_name = author.last_name or last_name
                        author.save()
                        book.authors.set([author])
                elif item["model"] == "pdcounter.author":
                    if pass_n != 1:
                        continue
                    slug = item["fields"]["slug"]
                    author, created = Author.objects.get_or_create(slug=slug)
                    if not author.first_name and not author.last_name:
                        author.first_name, author.last_name = parse_name(
                            item["fields"]["name"]
                        )
                        author.year_of_death = (
                            author.year_of_death or item["fields"]["death"]
                        )
                        author.notes = author.notes or item["fields"]["description"]
                        author.gazeta_link = (
                            author.gazeta_link or item["fields"]["gazeta_link"]
                        )
                        author.save()
                        wiki_link = item["fields"]["wiki_link"]
                        assert not wiki_link  # Welp
                elif item["model"] == "catalogue.book":
                    if pass_n != 2:
                        continue
                    if item["fields"]["parent"]:
                        continue
                    print(item["fields"]["slug"])
                    slug = item["fields"]["slug"]
                    book, created = Book.objects.get_or_create(slug=slug)
                    book.title = book.title or item["fields"]["title"]
                    book.language = book.language or item["fields"]["language"]
                    book.gazeta_link = book.gazeta_link or item["fields"]["gazeta_link"]
                    if item["fields"]["wiki_link"]:
                        book.wikidata = (
                            book.wikidata
                            or find_wikidata(item["fields"]["wiki_link"], "pl")
                            or ""
                        )

                    extra_info = json.loads(item["fields"]["extra_info"])
                    if book.pd_year is None and extra_info.get(
                        "released_to_public_domain_at"
                    ):
                        book.pd_year = int(
                            extra_info["released_to_public_domain_at"].split("-", 1)[0]
                        )

                    book.save()

                    if not book.authors.exists():
                        authors = []
                        for astr in extra_info.get("authors", []):
                            parts = astr.split(", ")
                            if len(parts) == 1:
                                first_name = parts[0]
                                last_name = ""
                            else:
                                last_name, first_name = parts
                            aslug = slugify(f"{first_name} {last_name}".strip())
                            author = (
                                Author.objects.filter(slug=aslug).first()
                                or Author.objects.filter(
                                    first_name=first_name, last_name=last_name
                                ).first()
                                or Author.objects.filter(name_de=astr).first()
                                or Author.objects.filter(name_lt=astr).first()
                            )
                            # Not trying to create the author or set properties, because here we don't know the dc:creator@xml:lang property.
                            if author is not None:
                                authors.append(author)
                        book.authors.set(authors)
                elif item["model"] == "catalogue.tag":
                    if pass_n != 1:
                        continue
                    if item["fields"]["category"] != "author":
                        continue
                    slug = item["fields"]["slug"]
                    author, created = Author.objects.get_or_create(slug=slug)
                    author.name_de = author.name_de or item["fields"]["name_de"] or ""
                    author.name_lt = author.name_lt or item["fields"]["name_lt"] or ""
                    if not author.first_name and not author.last_name:
                        author.first_name, author.last_name = parse_name(
                            item["fields"]["name_pl"]
                        )
                    author.culturepl_link = (
                        author.culturepl_link or item["fields"]["culturepl_link"] or ""
                    )
                    author.gazeta_link = (
                        author.gazeta_link or item["fields"]["gazeta_link"] or ""
                    )
                    author.description = (
                        author.description or item["fields"]["description_pl"] or ""
                    )
                    author.description_de = (
                        author.description_de or item["fields"]["description_de"] or ""
                    )
                    author.description_lt = (
                        author.description_lt or item["fields"]["description_lt"] or ""
                    )

                    if not author.wikidata:
                        for field, value in item["fields"].items():
                            if field.startswith("wiki_link_") and value:
                                wd = find_wikidata(value, field.rsplit("_", 1)[-1])
                                if wd:
                                    author.wikidata = wd
                                    break
                    author.save()

                else:
                    print(item)
                    break
