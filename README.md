====================
Platforma Redakcyjna
====================

Opis projektu
=============
Platforma to serwis służący do grupowej edycji książek na potrzeby serwisu WolneLektury.pl.

Instalacja i użycie
===================
#. Ściągnij i zainstaluj `pip <http://pypi.python.org/pypi/pip>`_
#. Przejdź do katalogu serwisu w konsoli
#. Zainstaluj wymagane biblioteki komendą::

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

Testy
====

    $ pip install -r requirements-test.txt
    $ python redakcja/manage.py test --settings=settings.test

JavaScript (wymagany node.js i xsltproc):

    $ npm install
    $ ./node_modules/.bin/mocha -u tdd $(find -name *_test.js)
