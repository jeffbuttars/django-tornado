from django.views.generic import TemplateView
from core.views import BaseTemplateView

from tornado import gen

class Index(BaseTemplateView):
    pass
# Index


class HttpClient(BaseTemplateView):
    pass
# HttpClient


class AsyncHttpClient(BaseTemplateView):

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
        ctx = self.base_data()
        ctx['treq'] = request.tornado_request

        return super(BaseTemplateView, self).get(request, **ctx)
    # get()
# HttpClient
