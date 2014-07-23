import datetime
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
    num_client_options = (1, 5, 10, 25, 50, 100)

    @gen.coroutine
    def get(self, request):
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
        num = int(request.GET.get('num_clients', 10))

        # Go and grab some web pages, asynchronously
        http_client = HttpClient()

        start_time = datetime.datetime.now()
        client_kwargs = {
            'connect_timeout': 60.0,
            'request_timeout': 60.0,
        }
        res = yield [http_client.get('http://yahoo.com', **client_kwargs) for x in xrange(num)]
        finish_time = datetime.datetime.now()

        web_results = []
        sync_total_time = 0
        for wr in res:
            web_results.append({
                'response': wr,
                'request': wr.request,
                'request_time': wr.request_time,
            })
            sync_total_time += wr.request_time
        # end for wr in res

        total_time = (finish_time - start_time).total_seconds()
        speedup = sync_total_time - total_time
        ctx = self.base_data(
            web_results=web_results,
            num_clients=num,
            start_time=start_time,
            finish_time=finish_time,
            total_time=total_time,
            sync_total_time=sync_total_time,
            speedup=speedup,
            speedup_percent=(speedup / total_time) * 100,
            num_client_options=self.num_client_options,
            treq=request.tornado_request,
        )

        myres = super(TestAsyncHttpClient, self).get(request, **ctx)
        logger.debug("Done with view, returning Django response")
        request.render(myres)
    # get()
# TestAsyncHttpClient
