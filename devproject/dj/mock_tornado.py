#!/usr/bin/env python
# encoding: utf-8

import logging

# Set up the logger
logger = logging.getLogger(__name__)
# Use a console handler, set it to debug by default
logger_ch = logging.StreamHandler()
logger.setLevel(logging.DEBUG)
log_formatter = logging.Formatter(('%(asctime)s %(levelname)s:%(process)s'
                                   ' %(lineno)s:%(module)s:%(funcName)s()'
                                   ' %(message)s'))
logger_ch.setFormatter(log_formatter)
logger.addHandler(logger_ch)

access_log = logger

access_log = logging.getLogger("tornado.access")
access_log.setLevel(logging.DEBUG)
access_log.addHandler(logger_ch)

app_log = logging.getLogger("tornado.application")
app_log.setLevel(logging.DEBUG)
app_log.addHandler(logger_ch)

gen_log = logging.getLogger("tornado.general")
gen_log.setLevel(logging.DEBUG)
gen_log.addHandler(logger_ch)


import os
import sys

this_dir = os.path.realpath(os.path.dirname(__file__))
ws_dir = os.path.realpath(os.path.join(this_dir, '../../doc/webservice'))
sys.path.insert(1, os.path.join(ws_dir, 'django'))
sys.path.insert(1, os.path.join(ws_dir, 'tornado'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dj.settings")

import tornado.ioloop
import tornado.web
import tornado.httpserver
import django
from django_tornado.core.handlers.dj_tornado import DjangoApplication


# class MainTornadoHandler(object):

#     def __init__(self, *args, **kwargs):
#         """todo: to be defined

#         :param *args: arg description
#         :type *args: type description
#         :param **kwargs: arg description
#         :type **kwargs: type description
#         """
#         logger.debug("%s::__init__ args:%s, kwargs:%s", self, args, kwargs)
#     # __init__()

#     def __call__(self, request):
#         """todo: Docstring for __call__
        
#         :param request: arg description
#         :type request: type description
#         :return:
#         :rtype:
#         """
#         logger.debug("%s::__call__ request: %s", self, request)
#         logger.debug("%s::__call__ dir(request): %s", self, dir(request))
#         logger.debug("%s::__call__ dir(request.connection): %s", self, dir(request.connection))
    
#         # body = bytes("You requested %s\n" % request.uri, 'utf8')
#         # message = bytes('HTTP/1.1 200 OK\r\n', 'utf8')
#         # message += bytes('Content-Length: %d\r\n\r\n%s' % (len(body), body), 'utf8')
#         body = "You requested %s\n" % request.uri
#         message = "HTTP/1.1 200 OK\r\n"
#         message += "Content-Length: %d\r\n\r\n%s" % (len(body), body)
#         request.write(bytes(message, 'utf8'))
#         request.finish()
#     # __call__()
# # MainTornadoHandler


def main():
    django.setup()

    # logger.debug("main")
    # logger.debug("main init handler")
    # handler = DjangoApplication()
    # logger.debug("main init server")
    # http_server = tornado.httpserver.HTTPServer(handler, xheaders=True)
    # logger.debug("main listen")
    # http_server.listen(8888)
    # logger.debug("main start")

    application = DjangoApplication()
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
# main()


if __name__ == '__main__':
    main()
