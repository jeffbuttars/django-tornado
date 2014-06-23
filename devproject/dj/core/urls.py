from django.conf.urls import patterns, include, url
import views

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.Index.as_view(), name="dj_index"),
)
