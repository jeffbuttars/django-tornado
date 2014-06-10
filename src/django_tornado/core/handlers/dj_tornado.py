import logging
# logger = logging.getLogger('django.request')
logger = logging.getLogger('django.debug')

import sys
import cgi
import codecs
import warnings
from io import BytesIO

import tornado.web

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
ISO_8859_1, UTF_8 = str('iso-8859-1'), str('utf-8')


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

        return response
    # __call__()

    def get(self, *args, **kwargs):
        logger.debug("TornadoHandler::get %s, %s", args, kwargs)
    # get()
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
    return script_name.decode(UTF_8)


def get_path_info(t_req):
    """
    Returns the HTTP request's PATH_INFO as a unicode string.
    """
    path_info = t_req.headers.get('PATH_INFO', '/')

    # It'd be better to implement URI-to-IRI decoding, see #19508.
    return path_info.decode(UTF_8)


# Looks like we'll need our own version of the tornado web Application class
# to do this well. The following is just a copy of current tornado source from
# Sat Jun  7 19:36:09 2014
# class Application(httputil.HTTPServerConnectionDelegate):
class DjangoApplication(tornado.web.Application):
    """A collection of request handlers that make up a web application.

    Instances of this class are callable and can be passed directly to
    HTTPServer to serve the application::

        application = web.Application([
            (r"/", MainPageHandler),
        ])
        http_server = httpserver.HTTPServer(application)
        http_server.listen(8080)
        ioloop.IOLoop.instance().start()

    The constructor for this class takes in a list of `URLSpec` objects
    or (regexp, request_class) tuples. When we receive requests, we
    iterate over the list in order and instantiate an instance of the
    first request class whose regexp matches the request path.
    The request class can be specified as either a class object or a
    (fully-qualified) name.

    Each tuple can contain additional elements, which correspond to the
    arguments to the `URLSpec` constructor.  (Prior to Tornado 3.2, this
    only tuples of two or three elements were allowed).

    A dictionary may be passed as the third element of the tuple,
    which will be used as keyword arguments to the handler's
    constructor and `~RequestHandler.initialize` method.  This pattern
    is used for the `StaticFileHandler` in this example (note that a
    `StaticFileHandler` can be installed automatically with the
    static_path setting described below)::

        application = web.Application([
            (r"/static/(.*)", web.StaticFileHandler, {"path": "/var/www"}),
        ])

    We support virtual hosts with the `add_handlers` method, which takes in
    a host regular expression as the first argument::

        application.add_handlers(r"www\.myhost\.com", [
            (r"/article/([0-9]+)", ArticleHandler),
        ])

    You can serve static files by sending the ``static_path`` setting
    as a keyword argument. We will serve those files from the
    ``/static/`` URI (this is configurable with the
    ``static_url_prefix`` setting), and we will serve ``/favicon.ico``
    and ``/robots.txt`` from the same directory.  A custom subclass of
    `StaticFileHandler` can be specified with the
    ``static_handler_class`` setting.

    """
    def __init__(self, handlers=None, default_host="", transforms=None,
                 **settings):
        logging.debug(
            "__init__(self, %s, %s, %s, %s)",
            handlers,
            default_host,
            transforms,
            settings)
        print(
            "DjangoApplication::__init__(self, %s, %s, %s, %s)" % (
            handlers,
            default_host,
            transforms,
            settings))

        self._app_handler = TornadoHandler

        super(DjangoApplication, self).__init__(
            handlers=handlers,
            default_host=default_host,
            transforms=transforms, settings=settings)


        # if transforms is None:
        #     self.transforms = []
        #     if settings.get("gzip"):
        #         self.transforms.append(GZipContentEncoding)
        # else:
        #     self.transforms = transforms
        # self.handlers = []
        # self.named_handlers = {}
        # self.default_host = default_host
        # self.settings = settings
        # self.ui_modules = {'linkify': _linkify,
        #                    'xsrf_form_html': _xsrf_form_html,
        #                    'Template': TemplateModule,
        #                    }
        # self.ui_methods = {}
        # self._load_ui_modules(settings.get("ui_modules", {}))
        # self._load_ui_methods(settings.get("ui_methods", {}))
        # if self.settings.get("static_path"):
        #     path = self.settings["static_path"]
        #     handlers = list(handlers or [])
        #     static_url_prefix = settings.get("static_url_prefix",
        #                                      "/static/")
        #     static_handler_class = settings.get("static_handler_class",
        #                                         StaticFileHandler)
        #     static_handler_args = settings.get("static_handler_args", {})
        #     static_handler_args['path'] = path
        #     for pattern in [re.escape(static_url_prefix) + r"(.*)",
        #                     r"/(favicon\.ico)", r"/(robots\.txt)"]:
        #         handlers.insert(0, (pattern, static_handler_class,
        #                             static_handler_args))
        # # if handlers:
        # #     self.add_handlers(".*$", handlers)

        # if self.settings.get('debug'):
        #     self.settings.setdefault('autoreload', True)
        #     self.settings.setdefault('compiled_template_cache', False)
        #     self.settings.setdefault('static_hash_cache', False)
        #     self.settings.setdefault('serve_traceback', True)

        # # Automatically reload modified modules
        # if self.settings.get('autoreload'):
        #     from tornado import autoreload
        #     autoreload.start()

    def listen(self, port, address="", **kwargs):
        logging.debug("listen(self, port, %s, %s)", address, kwargs)
        return super(DjangoApplication, self).listen(port, address, **kwargs)
        """Starts an HTTP server for this application on the given port.

        This is a convenience alias for creating an `.HTTPServer`
        object and calling its listen method.  Keyword arguments not
        supported by `HTTPServer.listen <.TCPServer.listen>` are passed to the
        `.HTTPServer` constructor.  For advanced uses
        (e.g. multi-process mode), do not use this method; create an
        `.HTTPServer` and call its
        `.TCPServer.bind`/`.TCPServer.start` methods directly.

        Note that after calling this method you still need to call
        ``IOLoop.instance().start()`` to start the server.
        # """
        # # import is here rather than top level because HTTPServer
        # # is not importable on appengine
        # from tornado.httpserver import HTTPServer
        # server = HTTPServer(self, **kwargs)
        # server.listen(port, address)

    def add_handlers(self, host_pattern, host_handlers):
        """Appends the given handlers to our handler list.

        Host patterns are processed sequentially in the order they were
        added. All matching patterns will be considered.
        """
        logging.debug("add_handlers(self, %s, %s)", host_pattern, host_handlers)
        return super(DjangoApplication, self).add_handlers(host_pattern, host_handlers)

        # if not host_pattern.endswith("$"):
        #     host_pattern += "$"
        # handlers = []
        # # The handlers with the wildcard host_pattern are a special
        # # case - they're added in the constructor but should have lower
        # # precedence than the more-precise handlers added later.
        # # If a wildcard handler group exists, it should always be last
        # # in the list, so insert new groups just before it.
        # if self.handlers and self.handlers[-1][0].pattern == '.*$':
        #     self.handlers.insert(-1, (re.compile(host_pattern), handlers))
        # else:
        #     self.handlers.append((re.compile(host_pattern), handlers))

        # for spec in host_handlers:
        #     if isinstance(spec, (tuple, list)):
        #         assert len(spec) in (2, 3, 4)
        #         spec = URLSpec(*spec)
        #     handlers.append(spec)
        #     if spec.name:
        #         if spec.name in self.named_handlers:
        #             app_log.warning(
        #                 "Multiple handlers named %s; replacing previous value",
        #                 spec.name)
        #         self.named_handlers[spec.name] = spec

    def add_transform(self, transform_class):
        logging.debug("add_transform(self, %s)", transform_class)
        super(DjangoApplication, self).add_transform(transform_class)
        # self.transforms.append(transform_class)

    def _get_host_handlers(self, request):
        logging.debug("_get_host_handlers(self, %s)", request)
        return super(DjangoApplication, self)._get_host_handlers(request)
        # host = request.host.lower().split(':')[0]
        # matches = []
        # for pattern, handlers in self.handlers:
        #     if pattern.match(host):
        #         matches.extend(handlers)
        # # Look for default host if not behind load balancer (for debugging)
        # if not matches and "X-Real-Ip" not in request.headers:
        #     for pattern, handlers in self.handlers:
        #         if pattern.match(self.default_host):
        #             matches.extend(handlers)
        # return matches or None

    def _load_ui_methods(self, methods):
        logging.debug("_load_ui_methods(self, %s)", methods)
        super(DjangoApplication, self)._load_ui_methods(methods)
        # if isinstance(methods, types.ModuleType):
        #     self._load_ui_methods(dict((n, getattr(methods, n))
        #                                for n in dir(methods)))
        # elif isinstance(methods, list):
        #     for m in methods:
        #         self._load_ui_methods(m)
        # else:
        #     for name, fn in methods.items():
        #         if not name.startswith("_") and hasattr(fn, "__call__") \
        #                 and name[0].lower() == name[0]:
        #             self.ui_methods[name] = fn

    def _load_ui_modules(self, modules):
        logging.debug("_load_ui_modules(self, %s)", modules)
        print("_load_ui_modules(self, %s)" % (modules))
        super(DjangoApplication, self)._load_ui_modules(modules)
        # if isinstance(modules, types.ModuleType):
        #     self._load_ui_modules(dict((n, getattr(modules, n))
        #                                for n in dir(modules)))
        # elif isinstance(modules, list):
        #     for m in modules:
        #         self._load_ui_modules(m)
        # else:
        #     assert isinstance(modules, dict)
        #     for name, cls in modules.items():
        #         try:
        #             if issubclass(cls, UIModule):
        #                 self.ui_modules[name] = cls
        #         except TypeError:
        #             pass

    def start_request(self, connection):
        logging.debug("start_request(self, %s)", connection)
        print("start_request(self, %s)" % connection)
        return super(DjangoApplication, self).start_request(connection)
        # # Modern HTTPServer interface
        # return _RequestDispatcher(self, connection)

    def __call__(self, request):
        logging.debug("__call__(self, %s)", request)
        print("__call__(self, %s)" % request)

        hdlr = self._app_handler()
        res = hdlr(request)

        print("DjangoApplication::__call__ result" % res)
        # return super(DjangoApplication, self).__call__(request)
        # # Legacy HTTPServer interface
        # dispatcher = _RequestDispatcher(self, None)
        # dispatcher.set_request(request)
        # return dispatcher.execute()

    def reverse_url(self, name, *args):
        logging.debug("reverse_url(self, %s, %s)", name, args)
        return super(DjangoApplication, self).reverse_url(name, *args)
        """Returns a URL path for handler named ``name``

        The handler must be added to the application as a named `URLSpec`.

        Args will be substituted for capturing groups in the `URLSpec` regex.
        They will be converted to strings if necessary, encoded as utf8,
        and url-escaped.
        """
        # if name in self.named_handlers:
        #     return self.named_handlers[name].reverse(*args)
        # raise KeyError("%s not found in named urls" % name)

    def log_request(self, handler):
        logging.debug("log_request(self, %s)", handler)
        return super(DjangoApplication, self).log_request(handler)
        """Writes a completed HTTP request to the logs.

        By default writes to the python root logger.  To change
        this behavior either subclass Application and override this method,
        or pass a function in the application settings dictionary as
        ``log_function``.
        """
        # if "log_function" in self.settings:
        #     self.settings["log_function"](handler)
        #     return
        # if handler.get_status() < 400:
        #     log_method = access_log.info
        # elif handler.get_status() < 500:
        #     log_method = access_log.warning
        # else:
        #     log_method = access_log.error
        # request_time = 1000.0 * handler.request.request_time()
        # log_method("%d %s %.2fms", handler.get_status(),
        #            handler._request_summary(), request_time)
