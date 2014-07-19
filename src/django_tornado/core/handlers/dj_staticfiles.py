import logging
# logger = logging.getLogger('django.request')
# logger = logging.getLogger('django.debug')

from django.conf import settings
from django.http import Http404
from django_tornado.core.handlers.dj_tornado import TornadoHandler
from django.utils.six.moves.urllib.parse import urlparse
from django.utils.six.moves.urllib.request import url2pathname

from django.contrib.staticfiles import utils
from django.contrib.staticfiles.views import serve


class StaticFilesHandler(TornadoHandler):
    """
    WSGI middleware that intercepts calls to the static files directory, as
    defined by the STATIC_URL setting, and serves those files.
    """
    def __init__(self, *args, **kwargs):
        self.base_url = urlparse(self.get_base_url())
        super(StaticFilesHandler, self).__init__(*args, **kwargs)

    def get_base_url(self):
        utils.check_settings()
        return settings.STATIC_URL

    def _should_handle(self, path):
        """
        Checks if the path should be handled. Ignores the path if:

        * the host is provided as part of the base_url
        * the request's path isn't under the media path (or equal)
        """
        # logger.debug("StaticFileHandler::_should_handle %s" % path)
        return path.startswith(self.base_url[2]) and not self.base_url[1]

    def file_path(self, url):
        """
        Returns the relative path to the media file on disk for the given URL.
        """
        relative_url = url[len(self.base_url[2]):]
        return url2pathname(relative_url)

    def serve(self, request):
        """
        Actually serves the request path.
        """
        # logger.debug("StaticFileHandler::serving %s" % request.path)
        return serve(request, self.file_path(request.path), insecure=True)

    def get_response(self, request):
        # logger.debug("StaticFileHandler::get_response %s", request.path)

        if self._should_handle(request.path):
            # logger.debug("StaticFileHandler::get_response should_handle")
            try:
                return self.serve(request)
            except Http404 as e:
                if settings.DEBUG:
                    from django.views import debug
                    return debug.technical_404_response(request, e)

        # logger.debug("StaticFileHandler::get_response not should_handle")
        return super(StaticFilesHandler, self).get_response(request)
