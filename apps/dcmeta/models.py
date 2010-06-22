from django.db import models
import eav.models
import pdb

# Some monkey patches to EAV:

# Allow dots & stuff
eav.models.slugify = lambda x: x

# Allow more characters 
eav.models.BaseSchema._meta.get_field_by_name("name")[0].max_length = 200

from django.contrib.auth.models import User
from django.contrib.contenttypes.generic import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from lxml import etree
from dcmeta.utils import RDFNS, common_prefixes, NamespaceDescriptor
import logging

logger = logging.getLogger("django.dcmeta")

class Description(eav.models.BaseEntity):
    """Collection of meta-data that can be assigned to an entity."""
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)

    about = GenericForeignKey()
    about_uri = models.TextField()

    attrs = GenericRelation('Attr', object_id_field="entity_id", content_type_field="entity_type")

    # shortcuts to EAV attributes
    dublincore = NamespaceDescriptor('http://purl.org/dc/elements/1.1/')
    marcrel = NamespaceDescriptor('http://www.loc.gov/loc.terms/relators/')

    @classmethod
    def get_schemata_for_model(self):
        return Schema.objects.all()

    @classmethod
    def import_rdf(cls, text):
        doc = etree.fromstring(text)
        xml_desc = doc.xpath('/rdf:RDF/rdf:Description', namespaces={"rdf": RDFNS.uri})

        if not xml_desc:
            raise ValueError("Invalid document structure.")

        xml_desc = xml_desc[0]

        desc = Description.objects.create(about_uri=xml_desc.get(RDFNS("about")))

        for xml_property in xml_desc.iterchildren():
            property, _created = Schema.objects.get_or_create(
                                name=xml_property.tag, datatype=Schema.TYPE_TEXT)
            property.save_attr(desc, xml_property.text)

        desc = Description.objects.get(pk=desc.pk)
        return desc

    def __getitem__(self, key):
        if not isinstance(key, tuple):
            raise ValueError
        ns, attr = key

        if ns in common_prefixes: # URI given, value stored as prefix
            ns = common_prefixes[ns]

        return getattr(self, "{%s}%s" % (ns, attr))

    def __setitem__(self, key, value):
        return setattr(self, "dc_" + key, value)

class Schema(eav.models.BaseSchema):
    pass

class Choice(eav.models.BaseChoice):
    """
        For properties with multiply values.
    """
    schema = models.ForeignKey(Schema, related_name='choices')

class Attr(eav.models.BaseAttribute):
    schema = models.ForeignKey(Schema, related_name='attrs')
    choice = models.ForeignKey(Choice, blank=True, null=True)
