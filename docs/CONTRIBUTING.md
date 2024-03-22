# Contributing

First off, thank you for considering contributing to SpokaneTech_Py!

The following is a set of guidelines for contributing to this project. These are just guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## Code of Conduct

This project and everyone participating in it are governed by the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [organizers@spokanetech.org](mailto:organizers@spokanetech.org).

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
- Merging contributions requires passing the checks configured with the CI. This includes running tests, linters, and other code quality tools successfully on the currently officially supported Python and Django versions.

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

`python-dotenv` will automatically load values in the `.env` file when Django's `manage.py` is used. Create a `.env` file from the template (**note: `.env` should never be checked in to source control!**):

```shell
cp .env.template .env
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

<details>
<summary>Full walkthrough</summary>

Generated using <a href="https://linux.die.net/man/1/script" target="_blank">script</a>. The highlighted lines are commands that should be ran in your terminal. Some output is truncated for brevity and is designated by "...".

```bash linenums="1" hl_lines="1 2 3 15 16 17 30 36"
$ python -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt -r requirements/dev.txt
Collecting asgiref==3.7.2
  Using cached asgiref-3.7.2-py3-none-any.whl (24 kB)
Collecting celery[redis]==5.3.6
  Using cached celery-5.3.6-py3-none-any.whl (422 kB)
Collecting discord.py==2.3.2
  Using cached discord.py-2.3.2-py3-none-any.whl (1.1 MB)
...
Installing collected packages: xlwt, webencodings, wcwidth, pytz, paginate, drf-dynamic-fields, cron-descriptor, watchdog, vine, urllib3, tzdata, typing-extensions, tomli, tinycss2, sqlparse, six, regex, redis, pyyaml, python-dotenv, pygments, pycparser, psycopg-binary, prompt-toolkit, pluggy, platformdirs, pillow, pathspec, packaging, multidict, mkdocs-material-extensions, mergedeep, MarkupSafe, markdown, iniconfig, idna, hurry.filesize, frozenlist, exceptiongroup, defusedxml, colorama, click, charset-normalizer, certifi, billiard, babel, attrs, async-timeout, yarl, requests, pyyaml-env-tag, python-dateutil, pytest, pymdown-extensions, psycopg, Jinja2, isodate, gunicorn, cssselect2, click-repl, click-plugins, click-didyoumean, cffi, asgiref, amqp, aiosignal, python-crontab, pytest-django, kombu, ghp-import, freezegun, Django, cryptography, cairocffi, azure-core, aiohttp, model-bakery, mkdocs, djangorestframework, django-timezone-field, django-storages, django-filter, dj-database-url, discord.py, celery, cairosvg, azure-storage-blob, mkdocs-material, djangorestframework-filters, django-celery-results, django-celery-beat, django-handyhelpers
Successfully installed Django-5.0.1 Jinja2-3.1.3 MarkupSafe-2.1.5 aiohttp-3.9.3 aiosignal-1.3.1 amqp-5.2.0 asgiref-3.7.2 async-timeout-4.0.3 attrs-23.2.0 azure-core-1.30.1 azure-storage-blob-12.19.1 babel-2.14.0 billiard-4.2.0 cairocffi-1.6.1 cairosvg-2.7.1 celery-5.3.6 certifi-2024.2.2 cffi-1.16.0 charset-normalizer-3.3.2 click-8.1.7 click-didyoumean-0.3.0 click-plugins-1.1.1 click-repl-0.3.0 colorama-0.4.6 cron-descriptor-1.4.3 cryptography-42.0.5 cssselect2-0.7.0 defusedxml-0.7.1 discord.py-2.3.2 dj-database-url-2.1.0 django-celery-beat-2.6.0 django-celery-results-2.5.1 django-filter-24.1 django-handyhelpers-0.3.20 django-storages-1.14.2 django-timezone-field-6.1.0 djangorestframework-3.15.0 djangorestframework-filters-1.0.0.dev0 drf-dynamic-fields-0.4.0 exceptiongroup-1.2.0 freezegun-1.4.0 frozenlist-1.4.1 ghp-import-2.1.0 gunicorn-21.2.0 hurry.filesize-0.9 idna-3.6 iniconfig-2.0.0 isodate-0.6.1 kombu-5.3.5 markdown-3.6 mergedeep-1.3.4 mkdocs-1.5.3 mkdocs-material-9.5.10 mkdocs-material-extensions-1.3.1 model-bakery-1.17.0 multidict-6.0.5 packaging-24.0 paginate-0.5.6 pathspec-0.12.1 pillow-10.2.0 platformdirs-4.2.0 pluggy-1.4.0 prompt-toolkit-3.0.43 psycopg-3.1.17 psycopg-binary-3.1.17 pycparser-2.21 pygments-2.17.2 pymdown-extensions-10.7.1 pytest-8.0.0 pytest-django-4.8.0 python-crontab-3.0.0 python-dateutil-2.9.0.post0 python-dotenv-1.0.1 pytz-2024.1 pyyaml-6.0.1 pyyaml-env-tag-0.1 redis-5.0.3 regex-2023.12.25 requests-2.31.0 six-1.16.0 sqlparse-0.4.4 tinycss2-1.2.1 tomli-2.0.1 typing-extensions-4.10.0 tzdata-2024.1 urllib3-2.2.1 vine-5.1.0 watchdog-4.0.0 wcwidth-0.2.13 webencodings-0.5.1 xlwt-1.3.0 yarl-1.9.4
WARNING: You are using pip version 22.0.4; however, version 24.0 is available.
You should consider upgrading via the '/Users/user/code/SpokaneTech_Py/venv/bin/python -m pip install --upgrade pip' command.
(venv) $ cp .env.template .env
(venv) $ cd src
(venv) $ python manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, django_celery_beat, django_celery_results, sessions, web
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
...
  Applying web.0001_initial... OK
  Applying web.0002_techgroup_event_group... OK
  Applying web.0003_event_created_at_event_updated_at_and_more... OK
  Applying web.0004_event_url... OK
(venv) $ python manage.py createsuperuser
Username (leave blank to use 'user'): admin
Email address: 
Password: 
Password (again): 
Superuser created successfully.
(venv) $ python manage.py runserver
Watching for file changes with StatReloader
Performing system checks...
System check identified no issues (0 silenced).
March 22, 2024 - 01:52:19
Django version 5.0.1, using settings 'spokanetech.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
^C
```

</details>

### Celery


The easiest way to run Celery locally is using Docker to run the message broker. We are using redis for our message broker. Make sure you have [Docker](https://docs.docker.com/get-docker/) installed and run the following docker command to start a redis container in the background:

```shell
docker compose up -d
```

In a separate terminal, run the Celery worker:

```shell
python -m celery --workdir ./src -A spokanetech.celery worker -B -l INFO
```

After running the Celery worker, you should see periodic tasks show in the [Django admin UI](http://127.0.0.1:8000/admin/django_celery_beat/periodictask/):

```shell
cd src
python manage.py runserver # (1)!
```

1.  Then navigate to the [Django admin UI](http://127.0.0.1:8000/admin/django_celery_beat/periodictask/)

![](./static/celery-admin.png)

Refer to our [Celery docs](./celery.md) for more information on how Celery works.

## Docs

When updating the docs locally, run the mkdocs server with `mkdocs serve`.

You can also build the docs with `mkdocs build`.

## Style Guide

Follow the coding style outlined in the [style guide](STYLE_GUIDE.md).

## License

By contributing, you agree that your contributions will be licensed under the [GNU-3 license](LICENSE.md).
