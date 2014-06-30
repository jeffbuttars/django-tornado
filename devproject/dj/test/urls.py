from django.conf.urls import patterns, include, url
import test.views

urlpatterns = patterns(
    '',
    url(r'^httpclient/$', test.views.Index.as_view(), name="dj_test_httpclient"),
    url(r'^$', test.views.HttpClient.as_view(), name="dj_test_index"),
)
