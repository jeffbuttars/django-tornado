# Tornado
An investigation to how an asynchronous tornado web service is handled within tornado.
We'll use the case of registering an application.
Included alongside this document is a test service that will be used for demonstration and tracing.


### Tornado 3.2.2
Tornado 4.X looks cool and offer a more fine grained interface, but for now we're using 3.2.2 .

We start by creating a handler class that has a callable instance.
The __call__ method of the instance will be called for each request and be given a
parameter `request` that is the incoming HTTP request from tornado.
It's up to that method to take it from there.

This is a raw handler in that it must write the entire response include headers, newlines, etc.
It calls `request.write` to write data to the output stream.
`request.write` can be called many times.
When `request.finished` is called the response is done and will be closed.

## Request Stack
Let's trace the stack of an incoming HTTP request from a browser through tornado

`BaseIOStream::_handle_events(callback, fd, events)`
Called by the IOLoop when an event has happened on the `fd` of the iostream
instance.

`BaseIOStream::_handle_read()`
Handle a read event on the iostream's fd

_many other methods and funcs called ..._

The iostream adds a wrapped request to the `IOLoop` via `add_callback`.
When the `IOLoop` runs the scheduled callback, the iostream picks back
up the execution.

`BaseIOStream::_run_callback(callback, *args)`
Runs the proper callback, in this case it's `_on_headers()` from an instance of:


:::python
    class HTTPConnection(object):
        """Handles a connection to an HTTP client, executing HTTP requests.

        We parse HTTP headers and bodies, and execute the request callback
        until the HTTP conection is closed.
        """

`HTTPConnection::_on_headers(data)`  
Parse the headers and create an `HttpRequest` object.  
Then the client code's request callback is called and passed the new request
object as a parameter.
