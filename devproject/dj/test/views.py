from tornado import gen
from django_tornado.http_client import HttpClient
from django.views.generic import TemplateView
from core.views import BaseTemplateView

import logging
logger = logging.getLogger('django.debug')


class Index(BaseTemplateView):
    pass
# Index


class TestHttpClient(BaseTemplateView):
    pass
# TestHttpClient


class TestAsyncHttpClient(BaseTemplateView):

    template_name = "test_async_httpclient.html"

    @gen.coroutine
    def get(self, request, *args, **kwargs):
        """todo: Docstring for get

        :param request: arg description
        :type request: type description
        :param *args: arg description
        :type *args: type description
        :param **kwargs: arg description
        :type **kwargs: type description
        :return:
        :rtype:
        """
        logger.debug("Start VIEW")

        # Go and grab a web page, asynchronously
        http_client = HttpClient()
        logger.debug("YIELD VIEW, self:%s" % (self,))
        res = yield http_client.get('http://google.com')
        logger.debug("AFTER YIELD self:%s" % (self,))

        logger.debug("http client result:\n%s\n", res)

        ctx = self.base_data(
            web_result=res,
            treq=request.tornado_request,
        )

        myres = super(TestAsyncHttpClient, self).get(request, **ctx)
        logger.debug("Done with view, returning Django response")
        request.render(myres)
    # get()
# TestAsyncHttpClient
