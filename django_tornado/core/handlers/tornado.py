from django import http
from django.core.handlers import base


class TornadoRequest(http.HttpRequest):
    """Docstring for TornadoRequest """
    
# TornadoRequest


class TornadoHandler(base.BaseHandler):
    """Docstring for TornadoHandler """

    request_class = TornadoRequest

    def __call__(self, t_req):
        """todo: Docstring for __call__

        :param arg1: arg description
        :type arg1: type description
        :return:
        :rtype:
        """

        pass
    # __call__()
# TornadoHandler
