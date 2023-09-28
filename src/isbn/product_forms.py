from collections import namedtuple

FormConfig = namedtuple('FormConfig', ['book', 'parent', 'product_form', 'product_form_detail'])

FORMS = [
    ('html', FormConfig(True, False, 'EC', 'E105')),
    ('txt', FormConfig(True, False, 'EB', 'E112')),
    ('pdf', FormConfig(True, True, 'EB', 'E107')),
    ('epub', FormConfig(True, True, 'ED', 'E101')),
    ('mobi', FormConfig(True, True, 'ED', 'E127')),
    ('mp3', FormConfig(False, False, 'AN', 'A103')),
    ('paperback', FormConfig(False, False, 'BC', '')),
]

