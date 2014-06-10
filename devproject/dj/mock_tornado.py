#!/usr/bin/env python
# encoding: utf-8

# import logging

# # Set up the logger
# logger = logging.getLogger('dj')
# # Use a console handler, set it to debug by default
# logger_ch = logging.StreamHandler()
# logger.setLevel(logging.DEBUG)
# log_formatter = logging.Formatter(('%(asctime)s %(levelname)s:%(process)s'
#                                    ' %(lineno)s:%(module)s:%(funcName)s()'
#                                    ' %(message)s'))
# logger_ch.setFormatter(log_formatter)
# logger.addHandler(logger_ch)


import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dj.settings")

import tornado.ioloop
import tornado.web
import tornado.httpserver
import django
from django_tornado.core.handlers.dj_tornado import DjangoApplication


# class MainDjangoHandler(tornado.web.RequestHandler):

#     def get(self, *args, **kwargs):
#         res = "MainDjangoHandler::get %s, %s" % (args, kwargs)
#         self.write(res)
#     # get()
# # MainDjangoHandler


def main():
    django.setup()

    dj_app = DjangoApplication()
    # w_server = tornado.httpserver.HTTPServer(DjangoApplication())
    # w_server.bind(8888, address="127.0.0.1")
    # w_server.start()
    dj_app.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
# main()


if __name__ == '__main__':
    main()
