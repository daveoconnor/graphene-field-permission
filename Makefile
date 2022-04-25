clean:
	rm -rf .eggs .cache .pytest_cache build dist graphene_field_permission.egg-info venv v

dev-install:
	virtualenv -p python3.9 venv
	. venv/bin/activate && pip install -r requirements.txt

dist-build:
	. venv/bin/activate && python setup.py sdist bdist_wheel && python -m pip install twine wheel && python setup.py sdist bdist_wheel


pypi-production-push:
	. venv/bin/activate && python -m twine upload -u __token__ -p ${LIVE_TOKEN} --non-interactive dist/*

pypi-test-push:
	. venv/bin/activate && python -m twine upload -u __token__ -p ${TEST_TOKEN} --repository testpypi dist/* --non-interactive --verbose

test:
	. venv/bin/activate && python setup.py test

test-all:
	bash testall.sh

