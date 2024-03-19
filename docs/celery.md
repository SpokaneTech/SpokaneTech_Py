# Celery

Celery is the standard package for doing background task processing in Python. It can run tasks outside of the WSGI/ASGI loop. Celery involves several differnent pieces to set up correctly:

<figure markdown="span">
  <img src="https://fly.io/django-beats/celery-async-tasks-on-fly-machines/assets/producer-broker-consumer-result-diagram.png" width="400" />
  <figcaption>An example Celery diagram from <a href="https://fly.io/django-beats/celery-async-tasks-on-fly-machines/#enter-celery" target="_blank">Fly.io</a></figcaption>
</figure>

Here are a few articles that help explain how Django and Celery work together:

- [First steps with Django: Using Celery with Django (OFFICIAL)](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html){ target="_blank" }
- [Asynchronous Tasks With Django and Celery (RealPython)](https://realpython.com/asynchronous-tasks-with-django-and-celery/){ target="_blank" }
- [Celery Async Tasks on Fly Machines (Fly.io)](https://fly.io/django-beats/celery-async-tasks-on-fly-machines/){ target="_blank" }

