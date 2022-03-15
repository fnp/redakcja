from datetime import date
import re
from django.conf import settings
from librarian.functions import lang_code_3to2
from librarian.html import transform_abstrakt
from librarian.builders import EpubBuilder, MobiBuilder
from librarian.cover import LegimiCornerCover, LegimiCover
import requests



fundraising=[
            "Książka, którą czytasz, pochodzi z <a href=\"https://wolnelektury.pl/\">Wolnych Lektur</a>. Naszą misją jest wspieranie dzieciaków w dostępie do lektur szkolnych oraz zachęcanie ich do czytania. Miło Cię poznać!",
            "Podoba Ci się to, co robimy? Jesteśmy organizacją pożytku publicznego. Wesprzyj Wolne Lektury drobną wpłatą: <a href=\"https://wolnelektury.pl/towarzystwo/\">wolnelektury.pl/towarzystwo/</a>",
            "Przyjaciele Wolnych Lektur otrzymują dostęp do prapremier wcześniej niż inni. Zadeklaruj stałą wpłatę i dołącz do Towarzystwa Przyjaciół Wolnych Lektur: <a href=\"https://wolnelektury.pl/towarzystwo/\">wolnelektury.pl/towarzystwo/</a>",
            "Informacje o nowościach w naszej bibliotece w Twojej skrzynce mailowej? Nic prostszego, zapisz się do newslettera. Kliknij, by pozostawić swój adres e-mail: <a href=\"https://wolnelektury.pl/newsletter/zapisz-sie/\">wolnelektury.pl/newsletter/zapisz-sie/</a>",
            "Przekaż 1% podatku na Wolne Lektury.<br/>\nKRS: 0000070056<br/>\nNazwa organizacji: Fundacja Nowoczesna Polska<br/>\nKażda wpłacona kwota zostanie przeznaczona na rozwój Wolnych Lektur."
]

class Legimi:
    #BASE_URL = 'https://wydawca.legimi.com'
    BASE_URL = 'https://panel.legimi.pl'
    LOGIN_URL = BASE_URL + '/publishers/membership'
    UPLOAD_URL = BASE_URL + '/administration/upload/start'
    CREATE_URL = BASE_URL + '/publishers/publications/create'
    EDIT_URL = BASE_URL + '/publishers/publications/edit/%s'
    EDIT_FILES_URL = BASE_URL + '/publishers/publications/editfiles/%s'
    
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

        cover = LegimiCornerCover(meta, width=1200).output_file()
        epub_file = EpubBuilder(cover=LegimiCover, fundraising=fundraising).build(wlbook).get_file()
        mobi_file = MobiBuilder(cover=LegimiCover, fundraising=fundraising).build(wlbook).get_file()

        book_data = {
            "Title": meta.title,
            "Author": ", ".join(p.readable() for p in meta.authors),
            "Year": meta.created_at[:4],

            'GenreId': '11', # TODO
            'Isbn': '',
            'LanguageLocale': lang_code_3to2(meta.language),

            'Description': '<p>—</p>',
        }
        if meta.isbn_html:
            isbn = meta.isbn_html
            if isbn.upper().startswith('ISBN '):
                isbn = isbn[5:]
            isbn = isbn.strip()
            book_data['Isbn'] = isbn

        files_data = {}

        abstract = wlbook.tree.find('.//abstrakt')
        if abstract is not None:
            book_data['Description'] = transform_abstrakt(abstract)
        

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


legimi = Legimi(
    settings.LEGIMI_USERNAME,
    settings.LEGIMI_PASSWORD,
    settings.LEGIMI_PUBLISHER_ID,
)
