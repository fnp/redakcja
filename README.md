====================
Platforma Redakcyjna
====================

Opis projektu
=============
Platforma to serwis służący do grupowej edycji książek na potrzeby serwisu WolneLektury.pl.

Instalacja i użycie
===================
#. Upewnij się, że masz Pythona w wersji co najmniej 3.5.
#. Stwórz i uruchom wirtualne środowisko:

        python3 -m venv ve
        . ve/bin/activate

#. Przejdź do katalogu serwisu w konsoli
#. Zainstaluj wymagane biblioteki komendą::

	pip install -r requirements/requirements.txt

#. Skopiuj zawartość pliku `src/redakcja/localsettings.sample` do `src/redakcja/localsettings.py` i zmień go zgodnie ze swoimi potrzebami.

#. Wypełnij bazę danych::

	src/manage.py migrate

#. Uruchom serwer deweloperski::

	src/manage.py runserver

#. Strategie wdrożeniowe opisane są w `Dokumentacji Django <http://docs.djangoproject.com/en/dev/howto/deployment/#howto-deployment-index>`_.


Testy
====

    $ pip install -r requirements-test.txt
    $ make test

JavaScript (wymagany node.js i xsltproc):

    $ npm install
    $ ./node_modules/.bin/mocha -u tdd $(find src -name *_test.js)
