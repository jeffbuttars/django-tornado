import django
from django_tornado.core.handlers.tornado import TornadoHandler


def get_tornado_application():
    """
    """

    django.setup()
    return TornadoHandler()
# get_tornado_application()
