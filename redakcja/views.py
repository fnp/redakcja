# -*- coding: utf-8 -*-
#
# This file is part of MIL/PEER, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .forms import RegistrationForm
from catalogue.models import Document
from organizations.models import Organization


def main(request):
    upcoming = Document.objects.filter(deleted=False).filter(publish_log=None)
    finished = Document.objects.filter(deleted=False).exclude(publish_log=None)
    organizations = Organization.objects.all()
    more_upcoming = upcoming.count() > 8
    more_finished = finished.count() > 8
    more_organizations = organizations.count() > 8
    upcoming = upcoming[:8]
    finished = finished[:8]
    organizations = organizations[:8]

    return render(request, 'main.html', {
        'finished': finished,
        'upcoming': upcoming,
        'organizations': organizations,
        'more_upcoming': more_upcoming,
        'more_finished': more_finished,
        'more_organizations': more_organizations,
    })


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            u = User.objects.create(
                    username=form.cleaned_data['email'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['email']
                )
            u.set_password(form.cleaned_data['password'])
            u.save()
            login(request, authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password']))
            send_mail(
                'Registered at MIL/PEER',
                '''You have been successfully registered at MIL/PEER with this e-mail address.

Thank you.

-- 
MIL/PEER team.''', 'milpeer@mdrn.pl', [form.cleaned_data['email']])
            return redirect('/')
    else:
        form = RegistrationForm()
    return render(request, 'registration.html', {'form': form})
