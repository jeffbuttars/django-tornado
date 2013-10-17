import functools
from tornado.ioloop import IOLoop


class ttask(object):

    """Docstring for ttask """
    __name__ = "ttask"

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
        """todo: Docstring for __call__

        :param *args: arg description
        :type *args: type description
        :param **kwargs: arg description
        :type **kwargs: type description
        :return:
        :rtype:
        """

        @functools.wraps(func)
        def decorated(self, *args, **kwargs):
            """todo: Docstring for decorated

            :param *args: arg description
            :type *args: type description
            :param **kwargs: arg description
            :type **kwargs: type description
            :return:
            :rtype:
            """

            return IOLoop.current().add_callback(func, args, kwargs)
        # decorated()

        return decorated
    #__call__()
# ttask
