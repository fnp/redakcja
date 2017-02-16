# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


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

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def get_projects(self):
        for project_line in self.projects.strip().split('\n'):
            parts = project_line.strip().split(None, 2)
            if not parts or not parts[0]:
                continue
            url, lang, desc = (parts + [''] * 2)[:3]
            yield url, lang, desc


@python_2_unicode_compatible
class UserCard(Card):
    user = models.OneToOneField(User, primary_key=True)

    def __str__(self):
        return self.user.get_full_name()

    def get_absolute_url(self):
        return reverse('organizations_user', args=[self.user.pk])


@python_2_unicode_compatible
class Organization(Card):
    name = models.CharField(max_length=1024)
    tags = models.ManyToManyField('catalogue.Tag', blank=True)

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
