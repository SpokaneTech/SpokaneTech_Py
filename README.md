# SpokaneTech
Home of [SpokaneTech.org](https://SpokaneTech.org), an online hub for Spokane's tech events and groups. It's not just a website; it's a community-driven, open-source initiative aimed at fostering learning and collaboration among aspiring and seasoned tech enthusiasts.


### Getting Started

Create and activate a virtual environment (may be `python3` or `python` on your machine):

Linux/MacOS
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows
```
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
