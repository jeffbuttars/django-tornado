from django.views.generic import TemplateView

class BaseTemplateView(TemplateView):
    template_name = "core_index.html"

    def base_data(self, **kwargs):
        bdata = {}
        bdata.update(kwargs)

        return bdata
    # base_data()

    def get(self, req):
        return super(BaseTemplateView, self).get(req, **self.base_data())
    # get()
# BaseTemplateView


class Index(BaseTemplateView):
    pass
# Index
