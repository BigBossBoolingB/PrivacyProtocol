# Distribution Process

This document outlines the process for packaging and distributing the Privacy Protocol.

## Building the Package

To build the package, run the following command from the root of the project:

```bash
python setup.py sdist bdist_wheel
```

This will create a `dist` directory containing the source distribution (`.tar.gz`) and a wheel (`.whl`).

## Testing the Distribution

Before publishing, you should test the distribution locally. You can do this by installing the wheel:

```bash
pip install dist/*.whl
```

You should then be able to import the `privacy_protocol` package and run the tests.

## Publishing to PyPI

To publish the package to PyPI, you will need to have an account on [pypi.org](https://pypi.org) and have `twine` installed (`pip install twine`).

Once you have everything set up, you can upload the distribution to PyPI:

```bash
twine upload dist/*
```

## Versioning Strategy

We use [Semantic Versioning](https://semver.org/) for versioning. The version number should be updated in `setup.py` before each release.

## Release Notes

Clear and concise release notes are important for communicating changes to users. Release notes should be created for each new version and should include a summary of the changes, as well as any breaking changes.
