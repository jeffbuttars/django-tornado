from optparse import make_option

import tornado.httpserver
import tornado.ioloop
import tornado.wsgi
from django.conf import settings
# import django.core.handlers.wsgi
from django.core.management.base import BaseCommand
from django_tornado.core.handlers.application import DjangoApplication


# We monkey patch the built in run with our own Tornado based version
def t_run(addr, port, t_app, ipv6=False, threading=False):
    server_address = (addr, port)
    if threading:
        httpd_cls = type(str('WSGIServer'), (socketserver.ThreadingMixIn, WSGIServer), {})
    else:
        httpd_cls = WSGIServer
    httpd = httpd_cls(server_address, WSGIRequestHandler, ipv6=ipv6)
    if threading:
        # ThreadingMixIn.daemon_threads indicates how threads will behave on an
        # abrupt shutdown; like quitting the server by the user or restarting
        # by the auto-reloader. True means the server will not wait for thread
        # termination before it quits. This will make auto-reloader faster
        # and will prevent the need to kill the server manually if a thread
        # isn't terminating correctly.
        httpd.daemon_threads = True
    # httpd.set_app(wsgi_handler)
    # httpd.serve_forever()

    t_app.listen(port)
    tornado.ioloop.IOLoop.instance().start()

import django.core.servers.basehttp
django.core.servers.basehttp.run = t_run

from django.core.management.commands.runserver import Command as RSCommand
naiveip_re = re.compile(r"""^(?:
(?P<addr>
    (?P<ipv4>\d{1,3}(?:\.\d{1,3}){3}) |         # IPv4 address
    (?P<ipv6>\[[a-fA-F0-9:]+\]) |               # IPv6 address
    (?P<fqdn>[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*) # FQDN
):)?(?P<port>\d+)$""", re.X)
DEFAULT_PORT = "8000"


# Use the builtin runserver command as our base
class Command(RSCommand):

    def get_handler(self, *args, **options):
        """
        Returns the default WSGI handler for the runner.
        """

        app_kwargs = {
            'debug': options['debug'],
            'autoreload': options['use_reloader'],
            'gzip': options['gzip'],
            'save_traceback': options['save_traceback'],
            'static': options['static'],
            'static_hash_cache': options['static_hash_cache'],
        }

        if options['debug'] and not options['static']:
            app_kwargs['staticfiles'] = True
        return = DjangoApplication(**app_kwargs)
    # get_handler()

    help = ("Starts a Tornado server instance for development or production")
    args = '[optional port number, or ipaddr:port]'

    # if settings.DEBUG:
    #     print("DEBUG True is default")

    option_list += (
        # make_option(
        #     '--debug',
        #     action='store_true',
        #     dest='debug',
        #     default=settings.DEBUG,
        #     help="Enable Tornado's debug mode.",
        # ),

        # make_option(
        #     '--port',
        #     dest='port',
        #     default=8000,
        #     help="Enable Tornado's debug mode.",
        # ),

        # make_option(
        #     '--autoreload',
        #     dest='autoreload',
        #     default=False,
        #     help="Enable Tornado's autoreload.",
        # ),

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
            '--static',
            dest='static',
            default=False,
            help="Enable Tornado's static file handling",
        ),

        make_option(
            '--static_hash_cache',
            dest='static_hash_cache',
            default=False,
            help="Enable Tornado's static_hash_cache option",
        ),
    )

    def inner_run(self, *args, **options):
        """Start a tornado ioloop running Django
        """
        # for opt in self.option_list:
        #     print(dir(opt))
        #     print(opt)
        # # end for opt in self.option_list

        # print(options)


        # http_server = tornado.httpserver.HTTPServer(tornado_app)
        # http_server.listen(options['port'])
        # tornado_app.listen(int(options['port']))
    # inner_run()
# Command
