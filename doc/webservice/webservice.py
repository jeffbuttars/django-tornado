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

import sys
import os

# make sure 'our' tornado and django is picked up first.
this_dir = os.path.realpath(os.path.dirname(__file__))
# sys.path.insert(1, os.path.join(this_dir, 'django'))
sys.path.insert(1, os.path.join(this_dir, 'tornado'))
print(sys.path)
# sys.meta_path.insert(0, sys.meta_path.pop(-1))
# print(sys.meta_path)

import tornado.httpserver
import tornado.ioloop
from tornado import httputil
from tornado.util import bytes_type, u

# logger.debug("%s", dir(httputil))
# class HttpServerHandler(httputil.HTTPServerConnectionDelegate):
#     """Not until tornado 4.0
#     """

#     def __init__(self, default_host="", transforms=None,
#                  **settings):

#         logger.debug("%s::__init__ default_host:%s, transforms: %s, settings: %s", self,
#                      default_host, transforms, settings
#                     )

#         if transforms is None:
#             self.transforms = []
#             if settings.get("gzip"):
#                 self.transforms.append(GZipContentEncoding)
#         else:
#             self.transforms = transforms
#         self.named_handlers = {}
#         self.default_host = default_host
#         self.settings = settings
#         self.ui_modules = {'linkify': _linkify,
#                            'xsrf_form_html': _xsrf_form_html,
#                            'Template': TemplateModule,
#                            }
#         self.ui_methods = {}
#         # self._load_ui_modules(settings.get("ui_modules", {}))
#         # self._load_ui_methods(settings.get("ui_methods", {}))
#         if self.settings.get("static_path"):
#             path = self.settings["static_path"]
#             static_url_prefix = settings.get("static_url_prefix",
#                                              "/static/")
#             static_handler_class = settings.get("static_handler_class",
#                                                 StaticFileHandler)
#             static_handler_args = settings.get("static_handler_args", {})
#             static_handler_args['path'] = path

#         if self.settings.get('debug'):
#             self.settings.setdefault('autoreload', True)
#             self.settings.setdefault('compiled_template_cache', False)
#             self.settings.setdefault('static_hash_cache', False)
#             self.settings.setdefault('serve_traceback', True)

#         # Automatically reload modified modules
#         if self.settings.get('autoreload'):
#             from tornado import autoreload
#             autoreload.start()

#     def add_transform(self, transform_class):
#         logger.debug("%s::add_transform transform_class: %s", self, transform_class)
#         self.transforms.append(transform_class)

#     def start_request(self, connection):
#         # Modern HTTPServer interface
#         logger.debug("%s::start_request connection: %s", self, connection)
#         return _RequestDispatcher(self, connection)

#     # def __call__(self, request):
#     #     """todo: Docstring for __call__
        
#     #     :param request: arg description
#     #     :type request: HTTPServerRequest or HTTPServerConnectionDelegate
#     #     :return:
#     #     :rtype:
#     #     """
    
#     #     pass
#     # # __call__()

#     def start_request(self, server_conn, request):
#         """
#         Modern HTTPServer interface

#         This method is called by the server when a new request has started.

#         :arg server_conn: is an opaque object representing the long-lived
#             (e.g. tcp-level) connection.
#         :arg request_conn: is a `.HTTPConnection` object for a single
#             request/response exchange.

#         This method should return a `.HTTPMessageDelegate`.
#         """
#         logger.debug("%s::start_request server_conn: %s, request_conn: %s", self,
#                     server_conn, request_conn)

#         message = "You requested %s\n" % request.uri
#         request.connection.write_headers(
#             httputil.ResponseStartLine('HTTP/1.1', 200, 'OK'),
#             {"Content-Length": str(len(message))})
#         request.connection.write(message)
#         request.connection.finish()

#         return _RequestDispatcher(self, connection)

#     def on_close(self, server_conn):
#         """This method is called when a connection has been closed.

#         :arg server_conn: is a server connection that has previously been
#             passed to ``start_request``.
#         """
#         logger.debug("%s::on_close server_conn: %s", self, server_conn)
#         pass

#     def log_request(self, handler):
#         """Writes a completed HTTP request to the logs.

#         By default writes to the python root logger.  To change
#         this behavior either subclass Application and override this method,
#         or pass a function in the application settings dictionary as
#         ``log_function``.
#         """
#         logger.debug("%s::log_request handler: %s", self, handler)

#         if "log_function" in self.settings:
#             self.settings["log_function"](handler)
#             return
#         if handler.get_status() < 400:
#             log_method = access_log.info
#         elif handler.get_status() < 500:
#             log_method = access_log.warning
#         else:
#             log_method = access_log.error
#         request_time = 1000.0 * handler.request.request_time()
#         log_method("%d %s %.2fms", handler.get_status(),
#                    handler._request_summary(), request_time)

# # HttpServerHandler
# logger.debug("%s::", self,)


class HttpServerHandler(object):
    """Docstring for HttpServerHandler """

    def __init__(self, *args, **kwargs):
        """todo: to be defined
        
        :param *args: arg description
        :type *args: type description
        :param **kwargs: arg description
        :type **kwargs: type description
        """
        logger.debug("%s::__init__ args:%s, kwargs:%s", self, args, kwargs)
    # __init__()

    def __call__(self, request):
        """todo: Docstring for __call__
        
        :param request: arg description
        :type request: type description
        :return:
        :rtype:
        """
        logger.debug("%s::__call__ request: %s", self, request)
        logger.debug("%s::__call__ dir(request): %s", self, dir(request))
        logger.debug("%s::__call__ dir(request.connection): %s", self, dir(request.connection))
        logger.debug("bytes_type %s", bytes_type)
    
        # body = bytes("You requested %s\n" % request.uri, 'utf8')
        # message = bytes('HTTP/1.1 200 OK\r\n', 'utf8')
        # message += bytes('Content-Length: %d\r\n\r\n%s' % (len(body), body), 'utf8')
        body = "You requested %s\n" % request.uri
        message = "HTTP/1.1 200 OK\r\n"
        message += "Content-Length: %d\r\n\r\n%s" % (len(body), body)
        request.write(bytes(message, 'utf8'))
        request.finish()
    # __call__()
    
# HttpServerHandler

# def handle_request(request):
#     message = "You requested %s\n" % request.uri
#     request.connection.write_headers(
#         httputil.ResponseStartLine('HTTP/1.1', 200, 'OK'),
#         {"Content-Length": str(len(message))})
#     request.connection.write(message)
#     request.connection.finish()


def main():
    logger.debug("main")
    # http_server = tornado.httpserver.HTTPServer(handle_request)
    logger.debug("main init handler")
    handler = HttpServerHandler()
    logger.debug("main init server")
    http_server = tornado.httpserver.HTTPServer(handler, xheaders=True)
    logger.debug("main listen")
    http_server.listen(8888)
    logger.debug("main start")
    tornado.ioloop.IOLoop.instance().start()
# main()

if __name__ == '__main__':
    main()
