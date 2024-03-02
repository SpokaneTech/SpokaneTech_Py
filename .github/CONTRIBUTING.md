# Contributing to SpokaneTech_Py

--8<-- [start:intro]
First off, thank you for considering contributing to SpokaneTech_Py!

The following is a set of guidelines for contributing to this project. These are just guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.
--8<-- [start:end]

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Pull Requests](#pull-requests)
- [Development](#development)
- [Style Guide](#style-guide)
- [License](#license)

--8<-- [start:mkdocs]
## Code of Conduct

This project and everyone participating in it are governed by the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [maintainer email].

## How Can I Contribute?

### Reporting Bugs

- Before creating bug reports, please check the [existing issues](https://github.com/SpokaneTech/SpokaneTech_Py/issues) as you might find that the issue has already been reported.
- When creating a bug report, please include a clear and concise description of the problem and steps to reproduce it.

### Suggesting Enhancements

- Before creating enhancement suggestions, please check the [list of open issues](https://github.com/SpokaneTech/SpokaneTech_Py/issues) as you might find that the suggestion has already been made.
- When creating an enhancement suggestion, please provide a detailed description and, if possible, an implementation proposal.

### Pull Requests

- Provide a clear and concise description of your pull request.
- Ensure you have tested your changes thoroughly.
- Add/update unittests as necessary.
- Make sure code quality tools run successfully. 

    Merging contributions requires passing the checks configured with the CI. This includes running tests, linters, and other code quality tools successfully on the currently officially supported Python and Django versions.

## Development

You can contribute to this project by forking it from GitHub and sending pull requests.

First [fork](https://help.github.com/en/articles/fork-a-repo) the
[repository](https://github.com/SpokaneTech/SpokaneTech_Py) and then clone it:

```shell
git clone git@github.com:<you>/SpokaneTech_Py.git
```

Create a virtual environment and install dependencies:

```shell
cd SpokaneTech_Py
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements/dev.txt
```

Run Django migrations:
```shell
cd src
python manage.py migrate
```

Create a Django superuser:
```shell
cd src
python manage.py createsuperuser
```

Run the Django development web server locally:
```shell
cd src
python manage.py runserver
```

Unit tests are located in each Django app under the tests directory and can be executed via pytest:
```shell
pytest
```


## Style Guide

Follow the coding style outlined in the [style guide](STYLE_GUIDE.md).

## License

By contributing, you agree that your contributions will be licensed under the [GNU-3 license](LICENSE.md).
--8<-- [start:end]
