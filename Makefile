.PHONY: deploy test


deploy: src/redakcja/localsettings.py
	pip install -r requirements/requirements.txt
	src/manage.py migrate --noinput
	src/manage.py collectstatic --noinput


.ONESHELL:
test:
	cd src
	./manage.py test --settings=redakcja.settings.test


.ONESHELL:
test_full:
	cd src
	coverage run --branch --source='.' ./manage.py test --settings=redakcja.settings.test_full; true
	coverage html -d ../htmlcov.new
	rm -rf ../htmlcov
	mv ../htmlcov.new ../htmlcov
	coverage report
	rm .coverage
