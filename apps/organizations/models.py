from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.template.loader import render_to_string
from django.utils import translation 
#from jsonfield import JSONField


countries = [
    ('intl', 'International'),
    ('at', 'Austria'),
    ('be', 'Belgium'),
    ('gb', 'Bulgaria'),
    ('hr', 'Croatia'),
    ('cy', 'Cyprus'),
    ('cz', 'Czech Republic'),
    ('dk', 'Denmark'),
    ('ee', 'Estonia'),
    ('fi', 'Finland'),
    ('fr', 'France'),
    ('de', 'Germany'),
    ('gr', 'Greece'),
    ('hu', 'Hungary'),
    ('ie', 'Ireland'),
    ('it', 'Italy'),
    ('lv', 'Latvia'),
    ('lt', 'Lithuania'),
    ('lu', 'Luxembourg'),
    ('mt', 'Malta'),
    ('nl', 'Netherlands'),
    ('pl', 'Poland'),
    ('pt', 'Portugal'),
    ('ro', 'Romania'),
    ('sk', 'Slovakia'),
    ('si', 'Slovenia'),
    ('es', 'Spain'),
    ('se', 'Sweden'),
    ('uk', 'United Kingdom'),
]


class Card(models.Model):
    logo = models.ImageField(upload_to='people/logo', blank=True)
    country = models.CharField(max_length=64, blank=True, choices=countries)
    www = models.URLField(blank=True)
    description = models.TextField(blank=True, default="")
    projects = models.TextField(blank=True, default="")

    preview_html = models.TextField(blank=True, default="")
    preview_html_pl = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        translation.activate('en')
        self.preview_html = render_to_string(self.preview_html_template, {
            'org': self
        })
        translation.activate('pl')
        self.preview_html_pl = render_to_string(self.preview_html_template, {
            'org': self
        })
        ret = super(Card, self).save(*args, **kwargs)
        return ret

    def get_projects(self):
        for project_line in self.projects.strip().split('\n'):
            parts = project_line.strip().split(' ', 2)
            if not parts or not parts[0]:
                continue
            url, lang, desc = (parts + [''] * 2)[:3]
            yield url, lang, desc

    def get_preview_html(self):
        lang = translation.get_language()
        try:
            p = getattr(self, "preview_html_%s" % lang)
            assert p
            return p
        except:
            return self.preview_html

@python_2_unicode_compatible
class UserCard(Card):
    preview_html_template = 'organizations/snippets/user.html'
    user = models.ForeignKey(User, unique=True, primary_key=True)

    def __str__(self):
        return str(self.user)

    def get_absolute_url(self):
        return reverse('organizations_user', args=[self.user.pk])


@python_2_unicode_compatible
class Organization(Card):
    preview_html_template = 'organizations/snippets/organization.html'

    name = models.CharField(max_length=1024)
    #logo = models.ImageField(upload_to='people/logo', blank=True)
    #country = models.CharField(max_length=64, blank=True, choices=countries)
    #www = models.URLField(blank=True)
    #description = models.TextField(blank=True, default="")
    ##projects = JSONField(default=[])
    #projects = models.TextField(blank=True, default="")

    #preview_html = models.TextField(blank=True, default="")

    #created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("organizations_main", args=[self.pk])

    def get_user_status(self, user):
        if not user.is_authenticated():
            return None
        try:
            member = self.membership_set.get(user=user)
        except Membership.DoesNotExist:
            return None
        else:
            return member.status

    def is_member(self, user):
        return self.get_user_status(user) in (
            Membership.Status.OWNER, Membership.Status.REGULAR)

    def is_owner(self, user):
        return self.get_user_status(user) == Membership.Status.OWNER

    def set_user_status(self, user, status):
        try:
            member = self.membership_set.get(user=user)
        except Membership.DoesNotExist:
            if status is not None:
                self.membership_set.create(user=user, status=status)
        else:
            if status is not None:
                member.status = status
                member.save()
            else:
                member.delete()


class Membership(models.Model):
    class Status:
        PENDING = 'pending'
        REGULAR = 'regular'
        OWNER = 'owner'

        choices = (
            (PENDING, 'Membership pending'),
            (REGULAR, 'Regular member'),
            (OWNER, 'Organizaition owner'),
        )

    organization = models.ForeignKey(Organization)
    user = models.ForeignKey(User)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.REGULAR)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('user', 'organization')
