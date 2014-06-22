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
sys.path.insert(1, os.path.join(this_dir, 'django'))
sys.path.insert(1, os.path.join(this_dir, 'tornado'))

import tornado.httpserver
import tornado.web
import tornado.ioloop


class DjangoTornadoRequestHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        logger.debug("DjangoTornadoRequestHandler::__init__() application: %s, request: %s, kwargs: %s",
                     application, request, kwargs)
        super(DjangoTornadoRequestHandler, self).__init__(application, request, **kwargs)
    # __init__()

    def _execute(self, transforms, *args, **kwargs):
        logger.debug("DjangoTornadoRequestHandler::_execute() transforms: %s, args: %s, kwargs: %s",
                     transforms, args, kwargs)
        return super(DjangoTornadoRequestHandler, self)._execute(transforms, *args, **kwargs)
    # _execute()

    def _execute_method(self):
        gen_log.debug("DjangoTornadoRequestHandler::_execute_method")
        if not self._finished:
            # method = getattr(self, self.request.method.lower())
            self._when_complete(self.django_handle_request(*self.path_args, **self.path_kwargs),
                                self._execute_finish)
            # self._when_complete(method(*self.path_args, **self.path_kwargs),
            #                     self._execute_finish)

    def django_handle_request(self, *args, **kwargs):
        """todo: Docstring for django_handle_request

        :param *args: arg description
        :type *args: type description
        :param **kwargs: arg description
        :type **kwargs: type description
        :return:
        :rtype:
        """
    
        gen_log.debug("DjangoTornadoRequestHandler::django_handle_request() args: %s, kwargs: %s",
                      args, kwargs)
        self.write("<html>Hello, world <br />")
        self.write(str(args))
        self.write("<br />")
        self.write(str(kwargs))
        self.write("<br />")
        self.write("</html>")
    # django_handle_request()

    def get(self):
        gen_log.debug("DjangoTornadoRequestHandler::get")
        self.write("Hello, world")
    # get()
# DjangoTornadoRequestHandler


class DjangoApplication(tornado.web.Application):
    def __init__(self, *args, **kwargs):
        """todo: to be defined
        
        :param *args: arg description
        :type *args: type description
        :param **kwargs: arg description
        :type **kwargs: type description
        """
        logger.debug("DjangoApplication::__init__() args: %s, kwargs: %s",
                     args, kwargs)

        self._django_req_cls = DjangoTornadoRequestHandler
        super(DjangoApplication, self).__init__(*args, **kwargs)
    # __init__()

    def __call__(self, request):
        """todo: Docstring for __call__
        
        :param request: arg description
        :type request: type description
        :return:
        :rtype:
        """
        logger.debug("DjangoApplication::__call__()request: %s", request)

        # return super(DjangoApplication, self).__call__(request)

        """Called by HTTPServer to execute the request."""
        gen_log.debug("Application__call__:: request:%s", request)

        transforms = [t(request) for t in self.transforms]

        handler_args = self.settings.get(
            'default_handler_args', {})
        handler = self._django_req_cls(self, request, **handler_args)

        # # If template cache is disabled (usually in the debug mode),
        # # re-compile templates and reload static files on every
        # # request so you don't need to restart to see changes
        # gen_log.debug("Application__call__:: handler template cache")
        # if not self.settings.get("compiled_template_cache", True):
        #     with RequestHandler._template_loader_lock:
        #         for loader in RequestHandler._template_loaders.values():
        #             loader.reset()
        # if not self.settings.get('static_hash_cache', True):
        #     StaticFileHandler.reset()

        gen_log.debug("Application__call__:: execute handler")
        handler._execute(transforms)

        gen_log.debug("Application__call__:: return handler")
        return handler
    # __call__()
# DjangoApplication


def main():
    logger.debug("main")
    application = DjangoApplication()
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
# main()

if __name__ == '__main__':
    main()
