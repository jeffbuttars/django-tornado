import logging
logger = logging.getLogger('django')

import functools
from tornado.ioloop import IOLoop
from tornado import gen


class ttask(object):

    """Run a task as a tornado callback. Greate for async background code.
    If tornado is not running, then things are run synchronously."""
    __name__ = "ttask"

    def __init__(self, *args, **kwargs):
        """When this gets more advance we can use this to setup
        more complicated features such as distributting to a true
        task service.

        :param *args: arg description
        :type *args: type description
        :param deadline: always delay this task by 'deadline'. This will be given to the
        add_timeout() method on the current IOLoop.
        :type deadline: float, seconds to delay this task by.
        :param **kwargs: arg description
        :type **kwargs: type description
        """
        self._args = args
        self._kwargs = kwargs

        self._deadline = kwargs.get('deadline')
    #__init__()

    def __call__(self, func):
        """todo: Docstring for __call__

        :param *args: arg description
        :type *args: type description
        :param **kwargs: arg description
        :type **kwargs: type description
        :return:
        :rtype:
        """

        logger.debug(
            "ttask decorate, IOLoop is running? %s", IOLoop.current()._running)

        if not IOLoop.current()._running:
            logger.debug("ttask running %s sync", func)

            @functools.wraps(func)
            def sync_decorated(*args, **kwargs):
                """Run the function synchronously
                """
                return IOLoop.current().run_sync(
                    functools.partial(func, *args, **kwargs))
            #sync_decorated()

            return sync_decorated

        logger.debug("ttask running %s async", func)

        if self._deadline:
            @functools.wraps(func)
            def deadline_decorated(*args, **kwargs):
                """Schedule the task as a timeout.
                """
                return IOLoop.current().add_timeout(
                    self._deadline,
                    functools.partial(func, *args, **kwargs)
                )
            # deadline_decorated()

            return deadline_decorated

        @functools.wraps(func)
        def decorated(*args, **kwargs):
            """todo: Docstring for decorated
            """
            # logger.debug(
            #     "Adding ttask %s to callback Q, args: %s, kwargs: %s", func, args, kwargs)
            return IOLoop.current().add_callback(func, *args, **kwargs)
        # decorated()

        return decorated
    #__call__()
# ttask


class ctask(object):

    """Run a task as a tornado callback. Great for async background code.
    If tornado is not running, then things are run synchronously.
    ctask will run the tornado.gen.coroutine on the decorated function before
    it's decorated with ctask. This is equivelant to decorting a function with
    tornado.gen.coroutine and ttask()
    """
    __name__ = "ctask"

    def __init__(self, *args, **kwargs):
        """When this gets more advance we can use this to setup
        more complicated features such as distributting to a true
        task service.

        :param *args: arg description
        :type *args: type description
        :param **kwargs: arg description
        :type **kwargs: type description
        """
        self._args = args
        self._kwargs = kwargs
    #__init__()

    def __call__(self, func):
        tt = ttask(*self._args, **self._kwargs)
        return tt(gen.coroutine(func))
    #__call__()
#ctask
