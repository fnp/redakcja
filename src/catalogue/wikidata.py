from datetime import date
from django.db import models
from django.db.models.signals import m2m_changed
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from wikidata.client import Client
from wikidata.datavalue import DatavalueError


class WikidataMixin(models.Model):
    wikidata = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('If you have a Wikidata ID, like "Q1337", enter it and save.'),
    )

    class Meta:
        abstract = True

    def save(self, **kwargs):
        super().save()
        if self.wikidata and hasattr(self, "Wikidata"):
            Wikidata = type(self).Wikidata
            client = Client()
            # Probably should getlist
            entity = client.get(self.wikidata)
            for attname in dir(Wikidata):
                if attname.startswith("_"):
                    continue
                wd = getattr(Wikidata, attname)

                model_field = self._meta.get_field(attname)
                if isinstance(model_field, models.ManyToManyField):
                    if getattr(self, attname).all().exists():
                        continue
                else:
                    if getattr(self, attname):
                        continue

                wdvalue = None
                if wd == "description":
                    wdvalue = entity.description.get("pl", str(entity.description))
                elif wd == "label":
                    wdvalue = entity.label.get("pl", str(entity.label))
                else:
                    try:
                        wdvalue = entity.get(client.get(wd))
                    except DatavalueError:
                        pass

                self.set_field_from_wikidata(attname, wdvalue)

        kwargs.update(force_insert=False, force_update=True)
        super().save(**kwargs)

    def set_field_from_wikidata(self, attname, wdvalue):
        if not wdvalue:
            return
        # Find out what this model field is
        model_field = self._meta.get_field(attname)
        if isinstance(model_field, models.ForeignKey):
            rel_model = model_field.related_model
            if issubclass(rel_model, WikidataMixin):
                # welp, we can try and find by WD identifier.
                wdvalue, created = rel_model.objects.get_or_create(wikidata=wdvalue.id)
                setattr(self, attname, wdvalue)
        elif isinstance(model_field, models.ManyToManyField):
            rel_model = model_field.related_model
            if issubclass(rel_model, WikidataMixin):
                wdvalue, created = rel_model.objects.get_or_create(wikidata=wdvalue.id)
                getattr(self, attname).set([wdvalue])
        else:
            # How to get original title?
            if isinstance(wdvalue, date):
                if isinstance(model_field, models.IntegerField):
                    wdvalue = wdvalue.year
            elif not isinstance(wdvalue, str):
                wdvalue = wdvalue.label.get("pl", str(wdvalue.label))
            setattr(self, attname, wdvalue)


class WikidataAdminMixin:
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.save()

    def wikidata_link(self, obj):
        if obj.wikidata:
            return format_html(
                '<a href="https://www.wikidata.org/wiki/{wd}" target="_blank">{wd}</a>',
                wd=obj.wikidata,
            )
        else:
            return ""

    wikidata_link.admin_order_field = "wikidata"
