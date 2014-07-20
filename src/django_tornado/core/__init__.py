

class TornadoVersionNotSupported(Exception):
    pass
# TornadoVersionNotSupported


import tornado
tornado_version_major = tornado.version_info[0]
tornado_version_minor = tornado.version_info[1]

if tornado_version_major == 3:
    if tornado_version_minor != 2:
        raise TornadoVersionNotSupported(
            "Tornado version %s is not supported by DjangoTornado." % tornado.version)
elif tornado_version_major == 4:
    if tornado_version_minor != 0:
        raise TornadoVersionNotSupported(
            "Tornado version %s is not supported by DjangoTornado." % tornado.version)
else:
    raise TornadoVersionNotSupported(
        "Tornado version %s is not supported by DjangoTornado." % tornado.version)
