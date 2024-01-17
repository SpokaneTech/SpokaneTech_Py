Create virtual environment.

```
python -m venv .venv

# Activate - Linux
source .venv/bin/activate

# Activate - Windows
.venv/scripts/activate.ps1

pip install -r requirements.txt
```

Run Migrations
```
cd src
python manage.py migrate
```

Run locally

```
cd src
python manage.py runserver
```
