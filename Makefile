clean:
	rm -rf .eggs .cache .pytest_cache build dist graphene_field_permission.egg-info venv py

dev-install:
	virtualenv -p python3.9 venv
	. venv/bin/activate && pip install -r requirements.txt

dist-build:
	. venv/bin/activate && python3 setup.py sdist bdist_wheel


pypi-production-push:
	python3.8 -m twine upload -u __token__ -p $LIVE_TOKEN --non-interactive dist/*

pypi-test-push:
	python3.8 -m twine upload -u __token__ -p $TEST_TOKEN --non-interactive --repository testpypi dist/*

test:
	. venv/bin/activate && python setup.py test

test-all:
	bash pypi-build.sh

