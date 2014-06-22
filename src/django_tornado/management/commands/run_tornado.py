from optparse import make_option

import tornado.httpserver
import tornado.ioloop
import tornado.wsgi
from django.conf import settings
# import django.core.handlers.wsgi
from django.core.management.base import BaseCommand
from django_tornado.core.handlers.dj_tornado import DjangoApplication


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

        make_option(
            '--autoreload',
            dest='autoreload',
            default=False,
            help="Enable Tornado's autoreload.",
        ),

        make_option(
            '--gzip',
            dest='gzip',
            default=False,
            help="Enable Tornado's gzip.",
        ),

        make_option(
            '--save_traceback',
            dest='save_traceback',
            default=False,
            help="Enable Tornado's save_traceback and print a traceback",
        ),

        make_option(
            '--static_hash_cache',
            dest='static_hash_cache',
            default=False,
            help="Enable Tornado's static_hash_cache option",
        ),
    )

    def handle(self, *args, **options):
        """Start a tornado ioloop running Django
        """
        # for opt in self.option_list:
        #     print(dir(opt))
        #     print(opt)
        # # end for opt in self.option_list

        # print(options)


        tornado_app = DjangoApplication(
            debug=options['debug'],
            autoreload=options['autoreload'],
            gzip=options['gzip'],
            save_traceback=options['save_traceback'],
            static_hash_cache=options['static_hash_cache'],
        )

        # http_server = tornado.httpserver.HTTPServer(tornado_app)
        # http_server.listen(options['port'])
        # tornado_app.listen(int(options['port']))
        tornado_app.listen(options['port'])
        tornado.ioloop.IOLoop.instance().start()
    # handle()
# Command
