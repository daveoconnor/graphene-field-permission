import setuptools
from os import sys

needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

with open('README.md') as readme:
    long_description = readme.read()

setuptools.setup(
    name="graphene-field-permission",
    version="0.0.9",
    author="Dave O'Connor",
    author_email="github@dead-pixels.org",
    description="A package to add field permission support for Graphene",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/daveoconnor/graphene-field-permission",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    tests_require=["pytest"],
    setup_requires=[
        "setuptools>=57.1.0",
        "twine>=3.4.1",
    ] + pytest_runner,

)
