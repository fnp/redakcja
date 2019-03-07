# -*- coding: utf-8 -*-
#
# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from catalogue.helpers import cached_in_field
from catalogue.models import Project
from dvcs import models as dvcs_models


class Image(dvcs_models.Document):
    """ An editable chunk of text. Every Book text is divided into chunks. """
    REPO_PATH = settings.CATALOGUE_IMAGE_REPO_PATH

    image = models.FileField(_('image'), upload_to='catalogue/images')
    title = models.CharField(_('title'), max_length=255, blank=True)
    slug = models.SlugField(_('slug'), unique=True)
    public = models.BooleanField(_('public'), default=True, db_index=True)
    project = models.ForeignKey(Project, null=True, blank=True)

    # cache
    _new_publishable = models.NullBooleanField(editable=False)
    _published = models.NullBooleanField(editable=False)
    _changed = models.NullBooleanField(editable=False)

    class Meta:
        app_label = 'catalogue'
        ordering = ['title']
        verbose_name = _('image')
        verbose_name_plural = _('images')
        permissions = [('can_pubmark_image', 'Can mark images for publishing')]

    # Representing
    # ============

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ("catalogue_image", [self.slug])

    def correct_about(self):
        return ["http://%s%s" % (
            Site.objects.get_current().domain,
            self.get_absolute_url()
            ),
            "http://%s%s" % (
                'obrazy.redakcja.wolnelektury.pl',
                self.get_absolute_url()
            )]

    # State & cache
    # =============

    def last_published(self):
        try:
            return self.publish_log.all()[0].timestamp
        except IndexError:
            return None

    def assert_publishable(self):
        from librarian.picture import WLPicture
        from librarian import NoDublinCore, ParseError, ValidationError

        class SelfImageStore(object):
            def path(self_, slug, mime_type):
                """Returns own file object. Ignores slug ad mime_type."""
                return open(self.image.path)

        publishable = self.publishable()
        assert publishable, _("There is no publishable revision")
        picture_xml = publishable.materialize()

        try:
            picture = WLPicture.from_bytes(
                    picture_xml.encode('utf-8'),
                    image_store=SelfImageStore)
        except ParseError, e:
            raise AssertionError(_('Invalid XML') + ': ' + str(e))
        except NoDublinCore:
            raise AssertionError(_('No Dublin Core found.'))
        except ValidationError, e:
            raise AssertionError(_('Invalid Dublin Core') + ': ' + str(e))

        valid_about = self.correct_about()
        assert picture.picture_info.about in valid_about, \
                _("rdf:about is not") + " " + valid_about[0]

    def publishable_error(self):
        try:
            return self.assert_publishable()
        except AssertionError, e:
            return e
        else:
            return None

    def accessible(self, request):
        return self.public or request.user.is_authenticated()

    def is_new_publishable(self):
        change = self.publishable()
        if not change:
            return False
        return not change.publish_log.exists()
    new_publishable = cached_in_field('_new_publishable')(is_new_publishable)

    def is_published(self):
        return self.publish_log.exists()
    published = cached_in_field('_published')(is_published)

    def is_changed(self):
        if self.head is None:
            return False
        return not self.head.publishable
    changed = cached_in_field('_changed')(is_changed)

    def touch(self):
        update = {
            "_changed": self.is_changed(),
            "_new_publishable": self.is_new_publishable(),
            "_published": self.is_published(),
        }
        Image.objects.filter(pk=self.pk).update(**update)

    # Publishing
    # ==========

    def publish(self, user):
        """Publishes the picture on behalf of a (local) user."""
        from base64 import b64encode
        import apiclient
        from catalogue.signals import post_publish

        self.assert_publishable()
        change = self.publishable()
        picture_xml = change.materialize()
        picture_data = open(self.image.path).read()
        apiclient.api_call(user, "pictures/", {
                "picture_xml": picture_xml,
                "picture_image_data": b64encode(picture_data),
            })
        # record the publish
        log = self.publish_log.create(user=user, change=change)
        post_publish.send(sender=log)
