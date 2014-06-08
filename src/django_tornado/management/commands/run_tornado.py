from optparse import make_option

import tornado.httpserver
import tornado.ioloop
import tornado.wsgi
from django.conf import settings
import django.core.handlers.wsgi
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    """Docstring for Command """

    help = ("Run Django on a Tornado instance.")

    # if settings.DEBUG:
    #     print("DEBUG True is default")

    option_list = BaseCommand.option_list + (
        make_option(
            '--debug',
            action='store_true',
            dest='debug',
            default=settings.DEBUG,
            help="Enable Tornado's debug mode.",
        ),

        make_option(
            '--port',
            dest='port',
            default=8000,
            help="Enable Tornado's debug mode.",
        ),
    )

    def handle(self, *args, **options):
        """Start a tornado ioloop running Django as it's
        WSGI App. Also, we add a static file handler to keep things happy.

        :param *args: arg description
        :type *args: type description
        :param **options: arg description
        :type **options: type description
        :return:
        :rtype:
        """

        wsgi_app = tornado.wsgi.WSGIContainer(
            django.core.handlers.wsgi.WSGIHandler())

        # Setup a tornado app to handle static files.
        tornado_app = tornado.web.Application(
            [
                (r'%s(.*)' % settings.STATIC_URL,
                 tornado.web.StaticFileHandler, {
                     'path': settings.STATIC_ROOT}),
                (r'.*',
                 tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
            ],
            debug=options['debug'],
        )

        http_server = tornado.httpserver.HTTPServer(tornado_app)
        http_server.listen(options['port'])
        tornado.ioloop.IOLoop.instance().start()
    # handle()
# Command
