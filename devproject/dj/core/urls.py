from django.conf.urls import patterns, include, url
import core.views

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', core.views.Index.as_view(), name="dj_index"),
)
