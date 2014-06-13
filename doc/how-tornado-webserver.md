# Tornado
An investigation to how an asynchronous tornado web service is handled within tornado. We'll use the case of registering an application. Included alongside this document is a test service that will be used for demonstration and tracing.


### Tornado 3.2.2
Tornado 4.X looks cool and offer a more fine grained interface, but for now we're using 3.2.2 .

We start by creating a handler class that has a callable instance. The __call__ method of the instance will be called for each request and be given a parameter `request` that is the incoming HTTP request from tornado. It's up to that method to take it from there.

This is a raw handler in that it must write the entire response include headers, newlines, etc. It calls `request.write` to write data to the output stream. `request.write` can be called many times. When `request.finished` is called the response is done and will be closed.
