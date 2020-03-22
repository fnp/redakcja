# Platforma Redakcyjna


## Opis projektu

Platforma to serwis służący do grupowej edycji książek na potrzeby serwisu WolneLektury.pl.


## Instalacja i użycie

1. Upewnij się, że masz Pythona w wersji co najmniej 3.5.
2. Stwórz i uruchom wirtualne środowisko:

```bash
python3 -m venv ve
. ve/bin/activate
```

3. Przejdź do katalogu serwisu w konsoli
4. Zainstaluj wymagane biblioteki komendą::

```bash
pip install -r requirements/requirements.txt
```

5. Skopiuj zawartość pliku `src/redakcja/localsettings.sample` do `src/redakcja/localsettings.py` i zmień go zgodnie ze swoimi potrzebami.

6. Wypełnij bazę danych::

```bash
src/manage.py migrate
```

7. Uruchom serwer deweloperski::

```bash
src/manage.py runserver
```

8. Strategie wdrożeniowe opisane są w [Dokumentacji Django](http://docs.djangoproject.com/en/dev/howto/deployment/#howto-deployment-index>).
   Do przygotowania wersji do wdrożenia możesz użyć komendy `make deploy`.


## Testy

```bash
pip install -r requirements-test.txt
make test
```

JavaScript (wymagany node.js i xsltproc):

```bash
npm install
./node_modules/.bin/mocha -u tdd $(find src -name *_test.js)
```
