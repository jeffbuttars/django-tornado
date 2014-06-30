from django.views.generic import TemplateView

class BaseTemplateView(TemplateView):
    template_name = "core_index.html"

    def base_data(self, data={}):
        bdata = {}
        bdata.update(data)

        return bdata
    # base_data()

    def get(self, req):
        return super(BaseTemplateView, self).get(req, **self.base_data())
    # get()
# BaseTemplateView


class Index(BaseTemplateView):
    pass
# Index
