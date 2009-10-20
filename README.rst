====================
Platforma Redakcyjna
====================

Opis projektu
=============
Platforma to serwis służący do grupowej edycji książek na potrzeby serwisu WolneLektury.pl.

Wymagania
=========
* `Django 1.1 <http://djangoproject.com/>`_
* `django-piston 0.2.3rc1 <http://bitbucket.org/jespern/django-piston/>`_
* `librarian 1.2 <http://redmine.nowoczesnapolska.org.pl/projects/show/librarian>`_
* `lxml 2.2.2 <http://codespeak.net/lxml/>`_
* `Mercurial 1.3.1 <http://www.selenic.com/mercurial/>`_
* `PIL 1.1.6 <http://www.pythonware.com/products/pil/>`_ (wymagane przez skrypt imgconv.py)
* `pngnq <http://pngnq.sourceforge.net/>`_ (wymagane przez skrypt imgconv.py)
* `zuber/django-cas-consumer <http://github.com/zuber/django-cas-consumer>`_ (wymagane do autoryzacji przez CAS)

Instalacja i użycie
===================
#. Ściągnij i zainstaluj `pip <http://pypi.python.org/pypi/pip>`_
#. Przejdź do katalogu serwisu w konsoli
#. Zainstaluj wymagane biblioteki (patrz sekcja wymagania_) komendą::

	pip install -r requirements.txt

#. Wypełnij bazę danych (Django poprosi o utworzenie pierwszego użytkownika)::

	./project/manage.py syncdb

#. Skopiuj zawartość pliku `project/localsettings.sample` do `project/localsettings.py` i zmień go zgodnie ze swoimi potrzebami.

#. Uruchom serwer deweloperski::

	./project/manage.py runserver

#. Zalecane jest serwowanie aplikacji przez `modwsgi <http://code.google.com/p/modwsgi/>`_ na serwerze `Apache2 <http://httpd.apache.org/>`_ przy pomocy załączonego skryptu `dispatch.fcgi`. Inne strategie wdrożeniowe opisane są w `Dokumentacji Django <http://docs.djangoproject.com/en/dev/howto/deployment/#howto-deployment-index>`_.

Wdrożenie
=========
#. Ściągnij i zainstaluj `fabric <http://docs.fabfile.org/>`_
#. Przejdź do katalogu serwisu w konsoli
#. Aby wdrożyć serwis na serwer deweloperski wpisz komendę::

	fab staging deploy
	
 Aby wdrożyć serwis na serwer produkcyjny wpisz::

	fab production deploy

