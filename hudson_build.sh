cd $WORKSPACE
virtualenv -q ve
source ./ve/bin/activate
pip install -q -E ./ve -r requirements.txt
pip install -q -E ./ve -r requirements-test.txt
django-admin.py test --settings=redakcja.settings.test
