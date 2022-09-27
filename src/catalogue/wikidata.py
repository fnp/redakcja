# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import date
from django.conf import settings
from django.db import models
from django.db.models.signals import m2m_changed
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from wikidata.client import Client
from wikidata.datavalue import DatavalueError
from modeltranslation.translator import translator
from modeltranslation.settings import AVAILABLE_LANGUAGES
from .wikimedia import Downloadable


class WikidataModel(models.Model):
    wikidata = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('If you have a Wikidata ID, like "Q1337", enter it and save.'),
    )

    class Meta:
        abstract = True

    def get_wikidata_property(self, client, entity, wd, lang):
        wdvalue = None

        if callable(wd):
            return wd(
                lambda next_arg:
                self.get_wikidata_property(
                    client, entity, next_arg, lang
                )
            )
        elif wd == "description":
            wdvalue = entity.description.get(lang, str(entity.description))
        elif wd == "label":
            wdvalue = entity.label.get(lang, str(entity.label))
        elif wd[0] == 'P':
            try:
                # TODO: lang?
                wdvalue = entity.get(client.get(wd))
            except DatavalueError:
                pass
        else:
            try:
                # wiki links identified as 'plwiki' etc.
                wdvalue = entity.attributes['sitelinks'][wd]['url']
            except KeyError:
                pass

        return wdvalue
        
        
    def wikidata_populate_field(self, client, entity, attname, wd, save, lang, force=False):
        if not force:
            model_field = self._meta.get_field(attname)
            if isinstance(model_field, models.ManyToManyField):
                if getattr(self, attname).all().exists():
                    return
            else:
                if getattr(self, attname):
                    return

        wdvalue = self.get_wikidata_property(client, entity, wd, lang)
            
        self.set_field_from_wikidata(attname, wdvalue, save=save)

    def wikidata_populate(self, save=True, force=False):
        Wikidata = type(self).Wikidata
        client = Client()
        # Probably should getlist
        entity = client.get(self.wikidata)
        for attname in dir(Wikidata):
            if attname.startswith("_"):
                continue
            wd = getattr(Wikidata, attname)

            self.wikidata_populate_attribute(client, entity, attname, wd, save=save, force=force)
        if hasattr(Wikidata, '_supplement'):
            for attname, wd in Wikidata._supplement(self):
                self.wikidata_populate_attribute(client, entity, attname, wd, save=save, force=force)

    def wikidata_fields_for_attribute(self, attname):
        field = getattr(type(self), attname)
        if type(self) in translator._registry:
            try:
                opts = translator.get_options_for_model(type(self))
            except:
                pass
            else:
                if attname in opts.fields:
                    tfields = opts.fields[attname]
                    for tf in tfields:
                        yield tf.name, tf.language
                    return

        yield attname, settings.LANGUAGE_CODE

    def wikidata_populate_attribute(self, client, entity, attname, wd, save, force=False):
        for fieldname, lang in self.wikidata_fields_for_attribute(attname):
            self.wikidata_populate_field(client, entity, fieldname, wd, save, lang, force=force)
                
    def save(self, **kwargs):
        am_new = self.pk is None

        super().save()
        if am_new and self.wikidata and hasattr(self, "Wikidata"):
            self.wikidata_populate()

        kwargs.update(force_insert=False, force_update=True)
        super().save(**kwargs)

    def set_field_from_wikidata(self, attname, wdvalue, save, language='pl'):
        if not wdvalue:
            return
        # Find out what this model field is
        model_field = self._meta.get_field(attname)
        skip_set = False
        if isinstance(model_field, models.ForeignKey):
            rel_model = model_field.related_model
            if issubclass(rel_model, WikidataModel):
                label = wdvalue.label.get(language, str(wdvalue.label))
                try:
                    wdvalue = rel_model.objects.get(wikidata=wdvalue.id)
                except rel_model.DoesNotExist:
                    wdvalue = rel_model(wikidata=wdvalue.id)
                    if save:
                        wdvalue.save()
                wdvalue._wikidata_label = label
                setattr(self, attname, wdvalue)
        elif isinstance(model_field, models.ManyToManyField):
            rel_model = model_field.related_model
            if issubclass(rel_model, WikidataModel):
                label = wdvalue.label.get(language, str(wdvalue.label))
                try:
                    wdvalue = rel_model.objects.get(wikidata=wdvalue.id)
                except rel_model.DoesNotExist:
                    wdvalue = rel_model(wikidata=wdvalue.id)
                    if save:
                        wdvalue.save()
                wdvalue._wikidata_label = label
                getattr(self, attname).set([wdvalue])
        else:
            # How to get original title?
            if isinstance(wdvalue, date):
                if isinstance(model_field, models.IntegerField):
                    wdvalue = wdvalue.year

            # If downloadable (and not save)?
            elif isinstance(wdvalue, Downloadable):
                if save:
                    wdvalue.apply_to_field(self, attname)
                    skip_set = True

            elif hasattr(wdvalue, 'label'):
                wdvalue = wdvalue.label.get(language, str(wdvalue.label))

            if not skip_set:
                setattr(self, attname, wdvalue)

    def wikidata_link(self):
        if self.wikidata:
            return format_html(
                '<a href="https://www.wikidata.org/wiki/{wd}" target="_blank">{wd}</a>',
                wd=self.wikidata,
            )
        else:
            return ""

    wikidata_link.admin_order_field = "wikidata"


class WikidataAdminMixin:
    class Media:
        css = {"screen": ("catalogue/wikidata_admin.css",)}
        js = ("catalogue/wikidata_admin.js",)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.save()
