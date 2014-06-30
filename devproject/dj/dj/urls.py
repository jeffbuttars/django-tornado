from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^test/', include('test.urls')),
    url(r'^', include('core.urls')),
)

urlpatterns += patterns(
    '',
    url(r'^', include('usethis_bootstrap.urls')),
)
