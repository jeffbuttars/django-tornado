import logging
# logger = logging.getLogger('django.request')
logger = logging.getLogger('django.debug')

import tornado.web

from django.conf import settings
from django.http.response import StreamingHttpResponse

from django_tornado.core.handlers.dj_staticfiles import StaticFilesHandler
from django_tornado.core.handlers.dj_tornado import TornadoHandler


class DjangoTornadoRequestHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        logger.debug(("DjangoTornadoRequestHandler::__init__() "
                      "application: %s, request: %s, kwargs: %s"),
                     application, request, kwargs)
        super(DjangoTornadoRequestHandler, self).__init__(application, request, **kwargs)

        if application.settings['staticfiles']:
            self._dj_handler = StaticFilesHandler()
        else:
            self._dj_handler = TornadoHandler()
    # __init__()

    def _execute_method(self):
        logger.debug("DjangoTornadoRequestHandler::_execute_method")
        if not self._finished:
            self._when_complete(self.django_handle_request(*self.path_args, **self.path_kwargs),
                                self._execute_finish)

    def django_handle_request(self, *args, **kwargs):
        """todo: Docstring for django_handle_request

        :param *args: arg description
        :type *args: type description
        :param **kwargs: arg description
        :type **kwargs: type description
        :return:
        :rtype:
        """

        logger.debug(("DjangoTornadoRequestHandler::django_handle_request()"
                      " args: %s, kwargs: %s"),
                     args, kwargs)

        # Now use the Django handler to run the request through Django
        logger.debug(("DjangoTornadoRequestHandler::django_handle_request()"
                      "calling tornadoHandler"))
        resp = self._dj_handler(self.request)

        # Update the status with the Django staus
        logger.debug(("DjangoTornadoRequestHandler::django_handle_request()"
                      "setting status tornadoHandler"))
        self.set_status(resp.status_code, resp.reason_phrase)

        # Update the headers with the Django headers
        logger.debug(("DjangoTornadoRequestHandler::django_handle_request()"
                      "copying headers"))

        for k, v in resp.items():
            logger.debug(("DjangoTornadoRequestHandler::django_handle_request()"
                          "setting header %s: %s") % (k, v))
            self.set_header(str(k), str(v))
        # end for k, v in resp.items

        # Write the Django response's cookies to the tornado response
        # headers
        for c in resp.cookies.values():
            logger.debug(("DjangoTornadoRequestHandler::django_handle_request()"
                        "adding COOKIE %s", c))
            self.add_header(
                str('Set-Cookie'), str(c.output(header=''))
            )

        # Write the Django generated content
        logger.debug(("DjangoTornadoRequestHandler::django_handle_request()"
                      "writing content"))

        try:
            self.write(resp.content)
        except AttributeError:
            for cont in resp.streaming_content:
                self.write(cont)
            # end for cont in resp

        self.finish()
    # django_handle_request()
# DjangoTornadoRequestHandler


# Looks like we'll need our own version of the tornado web Application class
# to do this well.
# Sat Jun  7 19:36:09 2014
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

        # Add our Django handler
        self._django_handlers = [
            (r'.*', DjangoTornadoRequestHandler),
        ]

        logger.debug("DjangoApplication::__init__() static_url: %s, static_path: %s",
                     settings.STATIC_URL, settings.STATIC_ROOT)

        if kwargs.pop('static', None):
            kwargs['static_url_prefix'] = settings.STATIC_URL
            kwargs['static_path'] = settings.STATIC_ROOT
                
        super(DjangoApplication, self).__init__(
            self._django_handlers,
            *args,
            **kwargs)
    # __init__()
# DjangoApplication
