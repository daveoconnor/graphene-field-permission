import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="graphene-field-permission",
    version="0.0.2",
    author="Dave O'Connor",
    author_email="github@dead-pixels.org",
    description="A package to add field permission support for Graphene",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/daveoconnor/graphene-field-permission",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
