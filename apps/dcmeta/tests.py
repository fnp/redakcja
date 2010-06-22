# -*- coding: utf-8
from django.test import TestCase
from dcmeta.models import Description

class ImportTests(TestCase):

    def test_basic_rdf(self):
        d = Description.import_rdf("""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:dc="http://purl.org/dc/elements/1.1/">
  <rdf:Description rdf:about="http://wolnelektury.pl/document/test">
    <dc:title>Simple test resource</dc:title>    
  </rdf:Description>
</rdf:RDF>""")
        self.assertEqual(d.attrs.count(), 1)
        self.assertEqual(d['http://purl.org/dc/elements/1.1/', 'title'], u"Simple test resource")

        # refetch the object
        d = Description.objects.get(about_uri="http://wolnelektury.pl/document/test")

        self.assertEqual(d.attrs.count(), 1)
        self.assertEqual(d['http://purl.org/dc/elements/1.1/', 'title'], u"Simple test resource")

        # access by prefix
        self.assertEqual(d['dc', 'title'], u"Simple test resource")

    def test_very_long_dc_property(self):
        NAME = "very_long_prop_name.with_dots.and.other_stuff_longer_then_50_chars"
        d = Description.import_rdf("""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:dc="http://purl.org/dc/elements/1.1/">
  <rdf:Description rdf:about="http://wolnelektury.pl/document/test">
    <dc:{0}>Simple test resource</dc:{0}>    
  </rdf:Description>
</rdf:RDF>""".format(NAME))

        self.assertEqual(d.attrs.count(), 1)
        self.assertEqual(d['dc', NAME], u"Simple test resource")

    def test_namespace_descriptors(self):
        d = Description.import_rdf("""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:dc="http://purl.org/dc/elements/1.1/"
         xmlns:marcrel="http://www.loc.gov/loc.terms/relators/">
  <rdf:Description rdf:about="http://wolnelektury.pl/document/test">
    <dc:title>Albatros</dc:title>    
    <marcrel:trl>Lange, Antoni</marcrel:trl>
    <marcrel:edt>Sekuła, Aleksandra</marcrel:edt>    
  </rdf:Description>
</rdf:RDF>""")

        self.assertEqual(d.dublincore.title, u"Albatros")
        self.assertEqual(list(d.marcrel), [
            ('trl', u"Lange, Antoni"), ('edt', u"Sekuła, Aleksandra"),
        ])

    def test_multiple_properties(self):
        d = Description.import_rdf("""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:dc="http://purl.org/dc/elements/1.1/"
         xmlns:marcrel="http://www.loc.gov/loc.terms/relators/">
  <rdf:Description rdf:about="http://wolnelektury.pl/document/test">
    <dc:title>Albatros</dc:title>    
    <marcrel:trl>Lange, Antoni</marcrel:trl>
    <marcrel:edt>Sekuła, Aleksandra</marcrel:edt>
    <marcrel:edt>Niedziałkowska, Marta</marcrel:edt>
    <marcrel:edt>Dąbek, Katarzyna</marcrel:edt>
  </rdf:Description>
</rdf:RDF>""")

        self.assertEqual(d['dc', 'title'], u"Albatros")
        self.assertEqual(d['marcrel', 'trl'], u"Lange, Antoni")
        self.assertEqual(d['marcrel', 'edt'], [
                u"Sekuła, Aleksandra",
                u"Niedziałkowska, Marta",
                u"Dąbek, Katarzyna",
        ])
