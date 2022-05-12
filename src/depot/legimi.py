from datetime import date
import re
from django.conf import settings
from librarian.functions import lang_code_3to2
from librarian.html import transform_abstrakt
from librarian.builders import EpubBuilder, MobiBuilder
from librarian.covers.marquise import MarquiseCover, LabelMarquiseCover
import requests
from slugify import slugify



fundraising=[
            "Książka, którą czytasz, pochodzi z <a href=\"https://wolnelektury.pl/\">Wolnych Lektur</a>. Naszą misją jest wspieranie dzieciaków w dostępie do lektur szkolnych oraz zachęcanie ich do czytania. Miło Cię poznać!",
            "Podoba Ci się to, co robimy? Jesteśmy organizacją pożytku publicznego. Wesprzyj Wolne Lektury drobną wpłatą: <a href=\"https://wolnelektury.pl/towarzystwo/\">wolnelektury.pl/towarzystwo/</a>",
            "Przyjaciele Wolnych Lektur otrzymują dostęp do prapremier wcześniej niż inni. Zadeklaruj stałą wpłatę i dołącz do Towarzystwa Przyjaciół Wolnych Lektur: <a href=\"https://wolnelektury.pl/towarzystwo/\">wolnelektury.pl/towarzystwo/</a>",
            "Informacje o nowościach w naszej bibliotece w Twojej skrzynce mailowej? Nic prostszego, zapisz się do newslettera. Kliknij, by pozostawić swój adres e-mail: <a href=\"https://wolnelektury.pl/newsletter/zapisz-sie/\">wolnelektury.pl/newsletter/zapisz-sie/</a>",
            "Przekaż 1% podatku na Wolne Lektury.<br/>\nKRS: 0000070056<br/>\nNazwa organizacji: Fundacja Nowoczesna Polska<br/>\nKażda wpłacona kwota zostanie przeznaczona na rozwój Wolnych Lektur."
]

description_add = '<p>Książkę polecają <a href="https://wolnelektury.pl">Wolne Lektury</a> — najpopularniejsza biblioteka on-line.</p>'


class Legimi:
    #BASE_URL = 'https://wydawca.legimi.com'
    BASE_URL = 'https://panel.legimi.pl'
    LOGIN_URL = BASE_URL + '/publishers/membership'
    UPLOAD_URL = BASE_URL + '/administration/upload/start'
    CREATE_URL = BASE_URL + '/publishers/publications/create'
    EDIT_URL = BASE_URL + '/publishers/publications/edit/%s'
    EDIT_FILES_URL = BASE_URL + '/publishers/publications/editfiles/%s'
    EDIT_SALE_URL = BASE_URL + '/publishers/publications/editsale/%s'

    CATEGORIES = {
        'Dla dzieci i młodzieży': 94,
        'Książki dla dzieci': 15,
        'Literatura młodzieżowa': 24,
        'Kryminał': 29,
        'Kryminał klasyczny': 31,
        'Kryminał współczesny': 32,
        'Kryminał historyczny': 30,
        'default': 8886,
        'Edukacja': 10,
        'Słowniki i leksykony': 14,
        'Encyklopedie': 13,
        'Lektury': 11,
        'Starożytność': 80,
        'Barok': 83,
        'Oświecenie': 84,
        'Dwudziestolecie międzywojenne': 88,
        'Średniowiecze': 81,
        'Współczesność': 90,
        'Modernizm': 87,
        'Pozytywizm': 86,
        'Renesans': 82,
        'Romantyzm': 85,
        'Młoda Polska': 89,
        'Podręczniki': 52,
        'Fantastyka i sci-fi': 25,
        'Fantastyka': 26,
        'Science fiction': 27,
        'Języki obce': 59,
        'Antyki i kolekcjonerstwo': 53,
        'Astrologia i wróżbiarstwo': 54,
        'Zdrowie i rodzina': 57,
        'Hobby': 55,
        'Medycyna i zdrowie': 58,
        'Psychologiczne': 78,
        'Styl': 56,
        'Humanistyka': 97,
        'Kultura i sztuka': 64,
        'Film': 66,
        'Muzyka': 65,
        'Eseje literackie': 49,
        'Historia': 60,
        'Styl życia': 73,
        'Wakacje i podróże': 69,
        'Dla mężczyzn': 79,
        'Sport': 76,
        'Obyczajowe i romanse': 93,
        'Humor': 68,
        'Obyczajowe': 35,
        'Powieść': 41,
        'Powieść przygodowa': 42,
        'Współczesna powieść przygodowa': 44,
        'Historyczna powieść przygodowa': 43,
        'Powieść historyczna': 46,
        'Powieść psychologiczna': 47,
        'Powieść religijna': 45,
        'Romans': 36,
        'Romans klasyczny': 38,
        'Romans współczesny': 39,
        'Literatura erotyczna': 40,
        'Romans historyczny': 37,
        'Dla kobiet': 77,
        'Sensacja, thriller, horror': 91,
        'Horror': 28,
        'Sensacja': 33,
        'Thriller': 34,
        'Aktualności': 70,
        'Czasopisma': 71,
        'Literatura faktu, reportaże, biografie': 92,
        'Literatura faktu': 16,
        'Biografie': 17,
        'Publicystyka': 20,
        'Dzienniki': 19,
        'Dokument, esej': 18,
        'Historia literatury i krytyka literacka': 23,
        'Literatura popularnonaukowa': 22,
        'Reportaż': 21,
        'Społeczno-polityczne': 72,
        'Poezja i dramat': 95,
        'Dramat': 48,
        'Poezja': 50,
        'Religia i duchowość': 51,
        'Nauka i nowe technologie': 98,
        'Nauka i technika': 61,
        'Nauki ścisłe': 62,
        'Nauki humanistyczne': 63,
        'Technologia i Internet': 75,
        'Specjalistyczne': 99,
        'Biznes i finanse': 1,
        'Ekonomia': 5,
        'Finanse': 6,
        'Zarządzanie': 3,
        'Marketing': 2,
        'Rozwój osobisty': 7,
        'Kariera i sukces zawodowy': 8,
        'Psychologia, motywacja': 9,
        'PR': 4,
        'Prawo': 67,
        'Branżowe': 74,
    }
    
    def __init__(self, username, password, publisher_id):
        self.username = username
        self.password = password
        self.publisher_id = publisher_id
        self._session = None

    @property
    def session(self):
        if self._session is None:
            session = requests.Session()
            response = session.post(
                self.LOGIN_URL,
                data={
                    'ValidationTrue': 'true',
                    'UserName': self.username,
                    'Password': self.password,
                })
            self._session = session
        return self._session
        
    def list(self):
        return self.session.get('https://wydawca.legimi.com/publishers/publications')
        
    def upload(self, content):
        response = self.session.post(
            self.UPLOAD_URL,
            files={
                "files": content,
            })
        model = response.json()['model']
        return {
            "name": model['Name'],
            "token": model['Token'],
            "url": model['Url'],
        }

#    name=files[]
#    filename
#    content-type
#    response: json
#     success: true
#     model.Url

    def send_book(self, book):
        wlbook = book.wldocument(librarian2=True)
        meta = wlbook.meta

        cover = LabelMarquiseCover(meta, width=1200).output_file()
        epub_file = EpubBuilder(cover=MarquiseCover, fundraising=fundraising).build(wlbook).get_file()
        mobi_file = MobiBuilder(cover=MarquiseCover, fundraising=fundraising).build(wlbook).get_file()

        book_data = {
            "Title": meta.title,
            "Author": ", ".join(p.readable() for p in meta.authors),
            "Year": str(date.today().year),

            'GenreId': str(self.get_genre(wlbook)),
            'Isbn': '',
            'LanguageLocale': lang_code_3to2(meta.language),

            'Description': self.get_description(wlbook),
        }
        if meta.isbn_html:
            isbn = meta.isbn_html
            if isbn.upper().startswith('ISBN '):
                isbn = isbn[5:]
            isbn = isbn.strip()
            book_data['Isbn'] = isbn

        files_data = {}

        cover_data = self.upload(
            (meta.url.slug + '.jpg', cover.get_file(), 'image/jpeg')
        )
        book_data.update({
            "Cover.Name": cover_data['name'],
            "Cover.Token": cover_data['token'],
            "Cover.Url": cover_data['url'],
        })

        epub_data = self.upload(
            (meta.url.slug + '.epub', epub_file, 'application/epub+zip')
        )
        files_data.update({
            'BookEpub.Token': epub_data['token'],
            'BookEpub.Name': epub_data['name'],
            'SampleEpubType': 'Generation',
        })

        mobi_data = self.upload(
            (meta.url.slug + '.mobi', mobi_file, 'application/x-mobipocket-ebook')
        )
        files_data.update({
            'BookMobi.Token': mobi_data['token'],
            'BookMobi.Name': mobi_data['name'],
        })
        
        if book.legimi_id:
            self.edit(
                book.legimi_id,
                book_data
            )
            self.edit_files(
                book.legimi_id,
                files_data
            )
        else:
            legimi_id = self.create_book(book_data, files_data)
            if legimi_id:
                book.legimi_id = legimi_id
                book.save(update_fields=['legimi_id'])

    def get_description(self, wlbook):
        description = ''
        abstract = wlbook.tree.find('.//abstrakt')
        if abstract is not None:
            description = transform_abstrakt(abstract)
        description += description_add
        description += '<p>'
        description += ', '.join(
            '<a href="https://wolnelektury.pl/katalog/autor/{}/">{}</a>'.format(
                slugify(p.readable()),
                p.readable(),
            )
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
            )
            for p in wlbook.meta.epochs
        ) + ' '
        description += 'Rodzaj: ' + ', '.join(
            '<a href="https://wolnelektury.pl/katalog/rodzaj/{}/">{}</a>'.format(
                slugify(p),
                p,
            )
            for p in wlbook.meta.kinds
        ) + ' '
        description += 'Gatunek: ' + ', '.join(
            '<a href="https://wolnelektury.pl/katalog/gatunek/{}/">{}</a>'.format(
                slugify(p),
                p,
            )
            for p in wlbook.meta.genres
        ) + '</p>'

        if wlbook.meta.audience:
            description += '<p><em>{}</em> to lektura szkolna.'.format(wlbook.meta.title)
            if wlbook.tree.find('//pe') is not None:
                description += '<br>Ebook <em>{title}</em> zawiera przypisy opracowane specjalnie dla uczennic i uczniów {school}.'.format(
                    title=wlbook.meta.title,
                    school='szkoły podstawowej' if wlbook.meta.audience == 'SP' else 'liceum i technikum'
                )
            description += '</p>'
        return description

    def get_genre(self, wlbook):
        if wlbook.meta.legimi and wlbook.meta.legimi in self.CATEGORIES:
            return self.CATEGORIES[wlbook.meta.legimi]
        for epoch in wlbook.meta.epochs:
            if epoch in self.CATEGORIES:
                return self.CATEGORIES[epoch]
        return self.CATEGORIES['Lektury']
    
    def create_book(self, book_data, files_data):
        data = {
            'createValidationTrue': 'true',
            'PublisherId': self.publisher_id,#3609954
            'IsLibraryPass': 'False',

            'SamplesGenerationType': 'Quantity',
            'SamplesGenerationPercent': '10',

            'EnterToTheMarketType': 'No',
            'EnterToTheMarketDate': date.today().strftime('%d.%m.%Y'),
            'HidingDate': '',
            'SalesNoLimitOption': 'false',
            'SalesNoLimitKindle': 'false',
            'SalesInStoreEbookGrossValue': '0,00',
            'SalesPromotion': 'False',
            'SalesPromotionGrossValue': '0,00',
            'SalesPromotionDatesRange.DateStart': '',
            'SalesPromotionDatesRange.DateEnd': '',
        }

        for form in 'Epub', 'Mobi', 'Pdf':
            data.update({
                f'Book{form}.Token': '',
                f'Book{form}.Name': '',
                f'Book{form}.StorageName': '',
                f'Book{form}.Order': '',

                f'Sample{form}Type': 'Files',
                f'Sample{form}.Token': '',
                f'Sample{form}.Name': '',
                f'Sample{form}.StorageName': '',
                f'Sample{form}.Order': '',
            })

        data.update(book_data)
        data.update(files_data)

        response = self.session.post(self.CREATE_URL, data=data)
        m = re.search(r'/(\d+)$', response.url)
        if m is not None:
            return m.group(1)

    def edit(self, legimi_id, data):
        current = {
            'ValidationTrue': 'true',
            'Is': legimi_id
        }

        current.update(data)
        
        self.session.post(
            self.EDIT_URL % legimi_id,
            data=current
        )

    def edit_files(self, legimi_id, files_data):
        current = {
            'ValidationTrue': 'true',
            'Id': legimi_id,
            'SamplesGenerationType': 'Quantity',
            'SamplesGenerationPercent': '10',
        }

        for form in 'Epub', 'Mobi', 'Pdf':
            current.update({
                f'Book{form}.Token': '',
                f'Book{form}.Name': '',
                f'Book{form}.StorageName': '',
                f'Book{form}.Order': '',

                f'Sample{form}.Type': 'Files',
                f'Sample{form}.Token': '',
                f'Sample{form}.Name': '',
                f'Sample{form}.StorageName': '',
                f'Sample{form}.Order': '',
            })

        current.update(files_data)
 
        response = self.session.post(
            self.EDIT_FILES_URL % legimi_id,
            data=current
        )

    def edit_sale(self, book):
        assert book.legimi_id

        words = book.wldocument().get_statistics()['total']['words_with_fn']

        price = settings.LEGIMI_SMALL_PRICE
        if words > settings.LEGIMI_SMALL_WORDS:
            price = settings.LEGIMI_BIG_PRICE

        abo = 'true' if words > settings.LEGIMI_BIG_WORDS else 'false'

        data = {
            'ValidationTrue': 'true',
            'Id': book.legimi_id,
            'SalesPromotionId': "0",
            'IsLibraryPass': "False",
            'OriginalEnterToTheMarketType': "No",
            'OriginalHidingDate': "",
            'OriginalEnterToTheMarketDate': "",
            'EnterToTheMarketType': "No",
            'EnterToTheMarketDate': "",
            'HidingDate': "",
            'SalesNoLimitOption': abo,
            'SalesNoLimitKindle': abo,
            'SalesInStoreEbookGrossValue': f'{price},00',
            'SalesPromotion': "False",
            'SalesPromotionGrossValue': "0,00",
            'SalesPromotionDatesRange.DateStart': "",
            'SalesPromotionDatesRange.DateEnd': "",
        }

        self.session.post(
            self.EDIT_SALE_URL % book.legimi_id,
            data=data
        )
        

legimi = Legimi(
    settings.LEGIMI_USERNAME,
    settings.LEGIMI_PASSWORD,
    settings.LEGIMI_PUBLISHER_ID,
)
