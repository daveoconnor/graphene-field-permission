#!/bin/bash

VERSIONS="$(pyenv versions --bare)"
echo $VERSIONS
for VERSION in $VERSIONS
	do
		export PYENV_VERSION=$VERSION
		echo "Python Version: $VERSION $(python --version)"
		pip install virtualenv
		python -m virtualenv --python=python$VERSION v/venv$VERSION
		source v/venv$VERSION/bin/activate
		pip install -r requirements.txt
		python setup.py test
		if [[ $? == 1 ]]; then
			exit 1
		fi;
		deactivate
done
