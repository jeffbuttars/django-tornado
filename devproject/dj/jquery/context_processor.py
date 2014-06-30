from django.conf import settings  # import the settingsfile
import os


def jquery_url(context):

    jquery_ver = getattr(settings, 'JQUERY_VER', '2.0.3')
    jquery_url = 'http://code.jquery.com/jquery-' + jquery_ver + '.min.js'

    if getattr(settings, 'DEBUG', False):
        static_url = getattr(settings, 'STATIC_URL', '/')
        static_url = os.path.join(static_url,
                                  'js',
                                  'jquery-' + jquery_ver + '.js')

    # return the value you want as a dictionnary.
    # you may add multiple values in there.
    return {
        'JQUERY_URL': jquery_url,
        'JQUERY_TAG': ('<script src="%s" type="text/javascript" '
                       'charset="utf-8"></script>') % jquery_url
    }


# def api_url(context):
#     return {
#         'API_URL': settings.API_URL,
#     }
