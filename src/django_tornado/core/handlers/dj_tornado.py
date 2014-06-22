import logging
# logger = logging.getLogger('django.request')
logger = logging.getLogger('django.debug')

import sys
# import platform
import cgi
import codecs
import warnings
from io import BytesIO
# import time
# import datetime

import tornado.web
# from tornado.escape import utf8
# from tornado import httputil

from django import http
from django.core import signals
from django.conf import settings
from django.core.handlers import base
from django.utils import datastructures
from django.utils.functional import cached_property
from django.core.urlresolvers import set_script_prefix
from django.utils.deprecation import RemovedInDjango19Warning
from django.utils.encoding import force_str, force_text
# Do we need this? I hope not, but wsgi uses it.
# from threading import Lock


# encode() and decode() expect the charset to be a native string.
# ISO_8859_1, UTF_8 = str('iso-8859-1'), str('utf-8')


class LimitedStream(object):
    '''
    LimitedStream wraps another stream in order to not allow reading from it
    past specified amount of bytes.
    '''
    def __init__(self, stream, limit, buf_size=64 * 1024 * 1024):
        self.stream = stream
        self.remaining = limit
        self.buffer = b''
        self.buf_size = buf_size

    def _read_limited(self, size=None):
        if size is None or size > self.remaining:
            size = self.remaining
        if size == 0:
            return b''
        result = self.stream.read(size)
        self.remaining -= len(result)
        return result

    def read(self, size=None):
        if size is None:
            result = self.buffer + self._read_limited()
            self.buffer = b''
        elif size < len(self.buffer):
            result = self.buffer[:size]
            self.buffer = self.buffer[size:]
        else:  # size >= len(self.buffer)
            result = self.buffer + self._read_limited(size - len(self.buffer))
            self.buffer = b''
        return result

    def readline(self, size=None):
        while b'\n' not in self.buffer and \
              (size is None or len(self.buffer) < size):
            if size:
                # since size is not None here, len(self.buffer) < size
                chunk = self._read_limited(size - len(self.buffer))
            else:
                chunk = self._read_limited()
            if not chunk:
                break
            self.buffer += chunk
        sio = BytesIO(self.buffer)
        if size:
            line = sio.readline(size)
        else:
            line = sio.readline()
        self.buffer = sio.read()
        return line


class TornadoRequest(http.HttpRequest):
    """Docstring for TornadoRequest """

    def __init__(self, t_req):
        """todo: to be defined
        
        :param t_req: arg description
        :type t_req: type description
        """

        self._tornado_request = t_req

        t_headers = t_req.headers

        script_name = get_script_name(t_req)
        # Sometimes PATH_INFO exists, but is empty (e.g. accessing
        # the SCRIPT_NAME URL without a trailing slash). We really need to
        # operate as if they'd requested '/'. Not amazingly nice to force
        # the path like this, but should be harmless.
        path_info = get_path_info(t_req) or '/'

        self.path_info = path_info
        self.path = '%s/%s' % (script_name.rstrip('/'), path_info.lstrip('/'))
        self.host = t_req.host

        self.META = t_headers
        self.META['PATH_INFO'] = path_info
        self.META['SCRIPT_NAME'] = script_name
        host_parts = t_req.host.rsplit(':', 1)
        self.META['SERVER_NAME'] = host_parts[0]
        self.META['SERVER_PORT'] = host_parts[1]

        # self.method = self.META['REQUEST_METHOD'].upper()
        self.META['REQUEST_METHOD'] = 'REQUEST_' + t_req.protocol.upper()
        self.method = 'REQUEST_' + t_req.protocol.upper()
        # if self.method not in ('GET', 'POST'):
        #     raise Exception("Fix METHOD header stuff!!!!!!")

        _, content_params = cgi.parse_header(t_headers.get('CONTENT_TYPE', ''))
        if 'charset' in content_params:
            try:
                codecs.lookup(content_params['charset'])
            except LookupError:
                pass
            else:
                self.encoding = content_params['charset']
        self._post_parse_error = False

        try:
            content_length = int(t_headers.get('CONTENT_LENGTH'), 0)
        except (ValueError, TypeError):
            content_length = 0

        self._stream = LimitedStream(t_req.body, content_length)
        # self._body = t_req.body
        self._read_started = False
        self.resolver_match = None
    # __init__()

    def _get_scheme(self):
        return self._tornado_request.protocol
    # _get_scheme()

    def _get_request(self):
        warnings.warn('`request.REQUEST` is deprecated, use `request.GET` or '
                      '`request.POST` instead.', RemovedInDjango19Warning, 2)
        if not hasattr(self, '_request'):
            self._request = datastructures.MergeDict(self.POST, self.GET)
        return self._request

    @cached_property
    def GET(self):
        # return self._tornado_request.query_arguments
        qry_args = self._tornado_request.query
        return http.QueryDict(qry_args, encoding=self._encoding)

    def _get_post(self):
        if not hasattr(self, '_post'):
            self._load_post_and_files()
        return self._post

    def _set_post(self, post):
        self._post = post

    @cached_property
    def COOKIES(self):
        raw_cookie = self._tornado_request.headers.get('Cookie', '')
        return http.parse_cookie(raw_cookie)

    def _get_files(self):
        if not hasattr(self, '_files'):
            self._load_post_and_files()
        return self._files

    POST = property(_get_post, _set_post)
    # POST = self._tornado_request.body_arguments
    FILES = property(_get_files)
    REQUEST = property(_get_request)
# TornadoRequest


class TornadoHandler(base.BaseHandler):
    """Docstring for TornadoHandler """

    # WSGI locks, Ideally, we don't run threaded. But
    # keep this here as a note for now in case this comes up later.
    # initLock = Lock()
    request_class = TornadoRequest

    def __call__(self, t_req):
        """todo: Docstring for __call__

        :param t_req: A tornado HTTPServerRequest instnace
        :type t_req: tornado HTTPServerRequest instnace
        :return:
        :rtype:
        """
        logger.debug("TornadoHandler __call__ %s", t_req)

        # Set up middleware if needed. We couldn't do this earlier, because
        # settings weren't available.
        if self._request_middleware is None:
            # with self.initLock:
            try:
                # Check that middleware is still uninitialized.
                if self._request_middleware is None:
                    self.load_middleware()
            except:
                # Unload whatever middleware we got
                self._request_middleware = None
                raise

        set_script_prefix(get_script_name(t_req))

        signals.request_started.send(sender=self.__class__)
        try:
            request = self.request_class(t_req)
        except UnicodeDecodeError:
            logger.warning('Bad Request (UnicodeDecodeError)',
                           exc_info=sys.exc_info(),
                           extra={
                               'status_code': 400,
                           }
                           )
            response = http.HttpResponseBadRequest()
        else:
            response = self.get_response(request)

        response._handler_class = self.__class__

        status = '%s %s' % (response.status_code, response.reason_phrase)
        response_headers = [(str(k), str(v)) for k, v in response.items()]
        for c in response.cookies.values():
            response_headers.append((str('Set-Cookie'), str(c.output(header=''))))

        # start_response(force_str(status), response_headers)
        print("TornadoHandler __call__ status: %s\n response_headers: %s" % (
            force_str(status), response_headers))
        print("TornadoHandler __call__ response %s" % (dir(response)))
        print("TornadoHandler __call__ response %s" % (response))
        # print("TornadoHandler __call__ response serialize %s" % (response.serialize()))

        return response
    # __call__()

    # def get(self, *args, **kwargs):
    #     logger.debug("TornadoHandler::get %s, %s", args, kwargs)
    # # get()
# TornadoHandler


def get_script_name(t_req):
    """
    Returns the equivalent of the HTTP request's SCRIPT_NAME header
    variable. If Apache mod_rewrite has been used, returns what would have been
    the script name prior to any rewriting (so it's the script name as seen
    from the client's perspective), unless the FORCE_SCRIPT_NAME setting is
    set (to anything).
    """
    if settings.FORCE_SCRIPT_NAME is not None:
        return force_text(settings.FORCE_SCRIPT_NAME)

    # If Apache's mod_rewrite had a whack at the URL, Apache set either
    # SCRIPT_URL or REDIRECT_URL to the full resource URL before applying any
    # rewrites. Unfortunately not every Web server (lighttpd!) passes this
    # information through all the time, so FORCE_SCRIPT_NAME, above, is still
    # needed.
    script_url = t_req.headers.get('SCRIPT_URL', '')
    if not script_url:
        script_url = t_req.headers.get('REDIRECT_URL', '')

    if script_url:
        path_info = t_req.headers.get('PATH_INFO', '')
        script_name = script_url[:-len(path_info)]
    else:
        script_name = t_req.headers.get('SCRIPT_NAME', '')

    # It'd be better to implement URI-to-IRI decoding, see #19508.
    # return script_name.decode(UTF_8)
    return script_name


def get_path_info(t_req):
    """
    Returns the HTTP request's PATH_INFO as a unicode string.
    """
    path_info = t_req.headers.get('PATH_INFO', '/')

    # It'd be better to implement URI-to-IRI decoding, see #19508.
    # return path_info.decode(UTF_8)
    return path_info


class DjangoTornadoRequestHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        logger.debug(("DjangoTornadoRequestHandler::__init__() "
                      "application: %s, request: %s, kwargs: %s"),
                     application, request, kwargs)
        super(DjangoTornadoRequestHandler, self).__init__(application, request, **kwargs)

        self._dj_handler = TornadoHandler()
    # __init__()

    # def _execute(self, transforms, *args, **kwargs):
    #     logger.debug(("DjangoTornadoRequestHandler::_execute() "
    #                  "transforms: %s, args: %s, kwargs: %s"),
    #                  transforms, args, kwargs)

    #     # return super(DjangoTornadoRequestHandler, self)._execute(transforms, *args, **kwargs)
    #     self._transforms = transforms
    #     try:
    #         if self.request.method not in self.SUPPORTED_METHODS:
    #             raise HTTPError(405)
    #         self.path_args = [self.decode_argument(arg) for arg in args]
    #         self.path_kwargs = dict((k, self.decode_argument(v, name=k))
    #                                 for (k, v) in kwargs.items())
    #         # If XSRF cookies are turned on, reject form submissions without
    #         # the proper cookie
    #         if self.request.method not in ("GET", "HEAD", "OPTIONS") and \
    #                 self.application.settings.get("xsrf_cookies"):
    #             self.check_xsrf_cookie()
    #         self._when_complete(self.prepare(), self._execute_method)
    #     except Exception as e:
    #         self._handle_request_exception(e)
    # # # _execute()

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
        resp = self._dj_handler(self.request)

        # Update the status with the Django staus
        self.set_status(resp.status_code, resp.reason_phrase)

        # Update the headers with the Django headers
        for k, v in resp.items():
            self.set_header(k, v)
        # end for k, v in resp.items

        # Write the Django generated content
        self.write(resp.content)

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

        # self._django_req_cls = DjangoTornadoRequestHandler
        # _django_app_ref = self
        def _fallback_wrapper(request, *args, **kwargs):
            logger.debug("_fallback_wrapper app:%s, request: %s, kwargs: %s",
                         self, request, kwargs)
            return DjangoTornadoRequestHandler(self, request, **kwargs)
        # _fallback_wrapper()

        # Add our Django handlers
        self._django_handlers = [
            # (r'%s(.*)' % settings.STATIC_URL,
            #  tornado.web.StaticFileHandler, {'path': settings.STATIC_ROOT}),
            (r'.*', DjangoTornadoRequestHandler),
            # (r'.*',
            #  tornado.web.FallbackHandler,
            #  dict(fallback=_fallback_wrapper)),
        ]

        super(DjangoApplication, self).__init__(
            self._django_handlers,
            static_url_prefix=getattr(settings, 'STATIC_URL', ''),
            static_path=getattr(settings, 'STATIC_ROOT', 'staticfiles'),
            *args,
            **kwargs)
    # __init__()

    # def __call__(self, request):
    #     """todo: Docstring for __call__
        
    #     :param request: arg description
    #     :type request: type description
    #     :return:
    #     :rtype:
    #     """
    #     logger.debug("DjangoApplication::__call__()request: %s", request)
    #     # super(DjangoApplication, self).__call__(request)

    #     return super(DjangoApplication, self).__call__(request)

    #     """Called by HTTPServer to execute the request."""
    #     logger.debug("Application__call__:: request:%s", request)

    #     transforms = [t(request) for t in self.transforms]

    #     handler_args = self.settings.get(
    #         'default_handler_args', {})
    #     handler = self._django_req_cls(self, request, **handler_args)

    #     # # If template cache is disabled (usually in the debug mode),
    #     # # re-compile templates and reload static files on every
    #     # # request so you don't need to restart to see changes
    #     # gen_log.debug("Application__call__:: handler template cache")
    #     # if not self.settings.get("compiled_template_cache", True):
    #     #     with RequestHandler._template_loader_lock:
    #     #         for loader in RequestHandler._template_loaders.values():
    #     #             loader.reset()
    #     # if not self.settings.get('static_hash_cache', True):
    #     #     StaticFileHandler.reset()

    #     logger.debug("Application__call__:: execute handler")
    #     handler._execute(transforms)

    #     logger.debug("Application__call__:: return handler")
    #     return handler
    # # __call__()
# DjangoApplication
