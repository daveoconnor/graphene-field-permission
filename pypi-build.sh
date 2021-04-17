#!/bin/bash
python3 -m virtualenv --python=python3.8 venv
source venv/bin/activate
python3 --version
python3 -m pip install -r requirements.txt
python3 -m pytest
if [[ $? == 1 ]]; then
	exit 1
fi;
python3 -m pip install twine
python3 setup.py sdist bdist_wheel
python3 -m twine upload -u __token__ -p $TEST_TOKEN --non-interactive --repository testpypi dist/*
python3 -m twine upload -u __token__ -p $LIVE_TOKEN --non-interactive dist/*
