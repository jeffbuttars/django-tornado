from django.views.generic import View

class BaseView(View):
    def get(self, req):
        return render(req, "core_index.html", {})
    # get()
# BaseView

class Index(BaseView):
    def get(self, req):
        return render(req, "core_index.html", {})
    # get()
# Index
