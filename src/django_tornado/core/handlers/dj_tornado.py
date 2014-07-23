from io import BytesIO


class LimitedStream(object):
    '''
    LimitedStream wraps another stream in order to not allow reading from it
    past specified amount of bytes.
    '''
    def __init__(self, stream, limit, buf_size=64 * 1024 * 1024):
        self.stream = stream
        self.remaining = limit
        self.buffer = b''
        self.buf_size = buf_size

    def _read_limited(self, size=None):
        if size is None or size > self.remaining:
            size = self.remaining
        if size == 0:
            return b''
        result = self.stream.read(size)
        self.remaining -= len(result)
        return result

    def read(self, size=None):
        if size is None:
            result = self.buffer + self._read_limited()
            self.buffer = b''
        elif size < len(self.buffer):
            result = self.buffer[:size]
            self.buffer = self.buffer[size:]
        else:  # size >= len(self.buffer)
            result = self.buffer + self._read_limited(size - len(self.buffer))
            self.buffer = b''
        return result

    def readline(self, size=None):
        while b'\n' not in self.buffer and \
              (size is None or len(self.buffer) < size):
            if size:
                # since size is not None here, len(self.buffer) < size
                chunk = self._read_limited(size - len(self.buffer))
            else:
                chunk = self._read_limited()
            if not chunk:
                break
            self.buffer += chunk
        sio = BytesIO(self.buffer)
        if size:
            line = sio.readline(size)
        else:
            line = sio.readline()
        self.buffer = sio.read()
        return line

from django_tornado.core.exceptions import TornadoVersionNotSupported

import tornado
tornado_version_major = tornado.version_info[0]
tornado_version_minor = tornado.version_info[1]

if tornado_version_major == 3:
    if tornado_version_minor != 2:
        raise TornadoVersionNotSupported(
            "Tornado version %s is not supported by DjangoTornado." % tornado.version)
    from django_tornado.core.handlers.tv32.dj_tornado import TornadoRequest, TornadoHandler
elif tornado_version_major == 4:
    if tornado_version_minor != 0:
        raise TornadoVersionNotSupported(
            "Tornado version %s is not supported by DjangoTornado." % tornado.version)
    from django_tornado.core.handlers.tv40.dj_tornado import TornadoRequest, TornadoHandler
else:
    raise TornadoVersionNotSupported(
        "Tornado version %s is not supported by DjangoTornado." % tornado.version)

