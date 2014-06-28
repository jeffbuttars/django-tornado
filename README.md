django-tornado
==============

Tornado integration for Django

This is currently in heavy development and the master branch is 
in now way stable and won't be for a little while.

# Features
* Use Tornado directly with Django (NO WSGI)
    * Tornado's Request objects are used directly to create Django Request objects and handle Django's responses
* `run_tornado` management command.
    * This command provides all the options of the `runserver` command plus some Tornado specific options
* Run production Django server instance(s) directly from the `manage.py` script. No need for Gunicorn and other WSGI services.
    * Utilize Tornado's process management for multi process runtime
* Enable fully asynchronous Django views!
    * Asynchronous API client calls in your views
    * Run code in your view after the request has been completed and responded to.
* Enable asynchronous tasks easily without using an external service like Celery.
    * Utilize Tornado's IOLoop as a run queue.
* Enable asynchronous timers to execute code at a given time or interval.
* More to Come!

# Implemented
* Use Tornado directly with Django (NO WSGI)
* `manage.py run_tornado` command


# TODO
* Support Tornado's `gen.coroutine` decorator on Django views
* Run production Django server instance(s) directly from the `manage.py` script. No need for Gunicorn and other WSGI services.
* Enable fully asynchronous Django views!
* Enable asynchronous tasks easily without using an external service like Celery.
* Enable asynchronous timers to execute code at a given time or interval.
