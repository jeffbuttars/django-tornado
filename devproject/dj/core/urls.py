from django.conf.urls import patterns, include, url
import core.views
from core.forms import BSAuthenticationForm

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', core.views.Index.as_view(), name="dj_index"),

    url(r'^login/$',
        'django.contrib.auth.views.login',
        {'template_name': 'core_login.html',
         "authentication_form": BSAuthenticationForm}),
    url(r'^logout/$',
        'django.contrib.auth.views.logout',
        {'next_page': '/'}),
)
