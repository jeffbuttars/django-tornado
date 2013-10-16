import logging
logger = logging.getLogger('django')

import tornado
from tornado.httpclient import HTTPClient, AsyncHTTPClient, HTTPError
from tornado.httputil import url_concat
from urllib.parse import urlencode


# class HttpClient(HTTPClient):
#     """Docstring for HttpClient """

#     def get(self, url, params, *kwargs):
#         """todo: Docstring for get

#         :param url: arg description
#         :type url: type description
#         :param kwargs: arg description
#         :type kwargs: type description
#         :return:
#         :rtype:
#         """

#         if params:
#             url = url_concat(url, params)

#         return self.fetch(url, method='GET', *kwargs)
#     #get()

#     def post(self, url, data=None, params=None, *kwargs):
#         """todo: Docstring for post

#         :param url: arg description
#         :type url: type description
#         :param *kwargs: arg description
#         :type *kwargs: type description
#         :return:
#         :rtype:
#         """

#         if params:
#             url = url_concat(url, params)

#         if data:
#             kwargs['body'] = tornado.escape.url_escape(data)

#         return self.fetch(url, method='POST', *kwargs)
#     #post()

#     def post_json(self, url, data, params=None, *kwargs):
#         """todo: Docstring for post_json

#         :param url: arg description
#         :type url: type description
#         :param data: arg description
#         :type data: type description
#         :param params: arg description
#         :type params: type description
#         :param *kwargs: arg description
#         :type *kwargs: type description
#         :return:
#         :rtype:
#         """
#         return self.post(url,
#                          data=tornado.escape.json_encode(data),
#                          params=params,
#                          headers={'Content-Type': 'application/json'},
#                          )
#     #post_json()
# #HttpClient

