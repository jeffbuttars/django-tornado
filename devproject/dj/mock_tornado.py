#!/usr/bin/env python
# encoding: utf-8

import logging

# Set up the logger
logger = logging.getLogger('dj')
# Use a console handler, set it to debug by default
logger_ch = logging.StreamHandler()
logger.setLevel(logging.DEBUG)
log_formatter = logging.Formatter(('%(asctime)s %(levelname)s:%(process)s'
                                   ' %(lineno)s:%(module)s:%(funcName)s()'
                                   ' %(message)s'))
logger_ch.setFormatter(log_formatter)
logger.addHandler(logger_ch)

import os

import tornado.ioloop
import tornado.web
import django
from django_tornado.core.handlers.dj_tornado import DjangoApplication


class MainDjangoHandler(tornado.web.RequestHandler):

    def get(self, *args, **kwargs):
        res = "MainDjangoHandler::get %s, %s" % (args, kwargs)
        #settings print res
        self.write(res)
    # get()
# MainDjangoHandler


django_application = DjangoApplication()


def main():

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dj.settings")

    # from django.core.wsgi import get_wsgi_application
    # application = get_wsgi_application()
    django.setup()

    django_application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
# main()


if __name__ == '__main__':
    main()
