import logging
logger = logging.getLogger('django')

import tornado
import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient
from tornado.httputil import url_concat
# from urllib.parse import urlencode


"""
This is a 'smart' HTTPClient wrapper that also makes requests
a bit simpler by borrowing much from the 'requests' module.

If a tornado IOLoop is running, then async requests are made.
Otherwise, tornado's run_sync() method is used to make the
calls synchronous.
"""


class HttpClient(object):
    """Docstring for HttpClient """

    def __init__(self):
        """todo: to be defined """

        self._ioloop = tornado.ioloop.IOLoop.current()
        self._hc = AsyncHTTPClient()

    #__init__()

    def get(self, url, params=None, **kwargs):
        """GET wrapper. Always returns a future.

        :param url: arg description
        :type url: type description
        :param kwargs: arg description
        :type kwargs: type description
        :return:
        :rtype:
        """

        if params:
            url = url_concat(url, params)

        return self._hc.fetch(url, method='GET', **kwargs)
    #get()

    def post(self, url, data=None, params=None, **kwargs):
        """todo: Docstring for post

        :param url: arg description
        :type url: type description
        :param *kwargs: arg description
        :type *kwargs: type description
        :return:
        :rtype:
        """

        if params:
            url = url_concat(url, params)

        if data:
            kwargs['body'] = data

        return self._hc.fetch(url, method='POST', **kwargs)
    #post()

    def post_json(self, url, data, params=None, **kwargs):
        """todo: Docstring for post_json

        :param url: arg description
        :type url: type description
        :param data: arg description
        :type data: type description
        :param params: arg description
        :type params: type description
        :param *kwargs: arg description
        :type *kwargs: type description
        :return:
        :rtype:
        """

        headers = {'Content-Type': 'application/json'}
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])

        kwargs['headers'] = headers

        logger.debug("POST url: %s, headers: %s, data: %s", url, headers, data)

        return self.post(url,
                         data=tornado.escape.json_encode(data),
                         params=params,
                         **kwargs
                         )
    #post_json()
#HttpClient
