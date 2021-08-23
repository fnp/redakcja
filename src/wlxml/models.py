from io import BytesIO
from django.apps import apps
from django.core.files import File
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from librarian import DocProvider
from librarian.parser import WLDocument as LegacyWLDocument
from librarian.builders import StandaloneHtmlBuilder, TxtBuilder
from librarian.document import WLDocument


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    type = models.CharField(max_length=255, choices=[
        ('section', _('Section, contains blocks')),
        ('div', _('Block element, like a paragraph')),
        ('span', _('Inline element, like an emphasis')),
        ('sep', _('Separator, has no content')),
        ('aside', _('Aside content, like a footnote')),
        ('verse', _('Verse element')),
    ], blank=True)
    similar_to = models.ForeignKey('self', models.PROTECT, null=True, blank=True)
    description = models.TextField(blank=True)
    example = models.TextField(blank=True)

    example_html = models.FileField(upload_to='wlxml/tag/example/html/', blank=True)
    example_pdf = models.FileField(upload_to='wlxml/tag/example/pdf/', blank=True)
    example_txt = models.FileField(upload_to='wlxml/tag/example/txt/', blank=True)

    # border_radius?
    editor_css = models.TextField(blank=True)
    editor_css_after = models.TextField(blank=True)

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('wlxml_tag', args=[self.name])
    ### allowed tags?

    def save(self, **kwargs):
        docbytes = b'''<utwor>

<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
<rdf:Description rdf:about="http://redakcja.wolnelektury.pl/documents/book/brudnopis/">

<dc:language xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">pol</dc:language>
<dc:creator xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">test</dc:creator>
<dc:title xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">test</dc:title>
<dc:date xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">test</dc:date>
<dc:publisher xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">test</dc:publisher>
<dc:identifier.url xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">test</dc:identifier.url>
<dc:rights xml:lang="pl" xmlns:dc="http://purl.org/dc/elements/1.1/">test</dc:rights>

</rdf:Description>
</rdf:RDF>

<opowiadanie>''' + self.example.encode('utf-8') + b'</opowiadanie></utwor>'


        doc = WLDocument(filename=BytesIO(docbytes))

        self.example_html.save(
            self.name + '.html',
            File(
                StandaloneHtmlBuilder().build(doc).get_file()),
            save=False)
        self.example_txt.save(
            self.name + '.txt',
            File(
                TxtBuilder().build(doc).get_file()),
            save=False)

        provider=DocProvider()
        legacy_doc = LegacyWLDocument.from_bytes(docbytes, provider=provider)

        self.example_pdf.save(
            self.name + '.pdf',
            File(legacy_doc.as_pdf().get_file()),
            save=False)
        

        super().save(**kwargs)

    

class Attribute(models.Model):
    tag = models.ForeignKey(Tag, models.CASCADE)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = _('attribute')
        verbose_name_plural = _('attribute')
    
        unique_together = [
            ('tag', 'name'),
        ]

    def __str__(self):
        return self.name

    
class TagUsage(models.Model):
    tag = models.ForeignKey(Tag, models.CASCADE)
    chunk = models.ForeignKey('documents.Chunk', models.CASCADE)

    class Meta:
        verbose_name = _('tag usage')
        verbose_name_plural = _('tags usage')
    
    def __str__(self):
        return f'{self.tag.name} @ {self.chunk.slug}'
        
    
    @classmethod
    def update_chunk(cls, chunk):
        tag_names = set()
        attribute_items = {}
        doc = WLDocument.from_bytes(chunk.materialize().encode('utf-8'))
        for element in doc.edoc.iter():
            tag_names.add(element.tag)
            for k, v in element.attrib.iteritems():
                attribute_items.setdefault(element.tag, set()).add((k, v))

        cls.objects.filter(chunk=chunk).exclude(tag__name__in=tag_names).delete()
        for tag_name in tag_names:
            tag, create = Tag.objects.get_or_create(name=tag_name)
            tu, created = cls.objects.get_or_create(tag=tag, chunk=chunk)

            new_attributes = attribute_items.get(tag_name, [])
            
            for attr in tu.attributeusage_set.all():
                key = (attr.attribute.name, value)
                if key not in new_attributes:
                    attr.delete()
                else:
                    new_attributes.delete(key)

            for k, v in new_attributes:
                attribute, created = tag.attribute_set.get_or_create(name=k)
                tu.attributeusage_set.create(attribute=attribute, value=v)


    @classmethod
    def update_all_chunks(cls):
        Chunk = apps.get_model('documents', 'Chunk')
        for chunk in Chunk.objects.all():
            cls.update_chunk(chunk)


class AttributeUsage(models.Model):
    tag_usage = models.ForeignKey(TagUsage, models.CASCADE)
    attribute = models.ForeignKey(Attribute, models.CASCADE)
    value = models.CharField(max_length=2048, blank=True)

    class Meta:
        verbose_name = _('attribute usage')
        verbose_name_plural = _('attributes usage')
    
