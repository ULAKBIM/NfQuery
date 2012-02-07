#!/usr/local/bin/python

"""
Created on 11/4/2009 by Mark Barfield

It is licensed under the Apache License, Version 2.0
(http://www.apache.org/licenses/LICENSE-2.0.html).
"""

from jsonrpclib import SimpleJSONRPCServer
import BaseHTTPServer
import SocketServer
import sys
import socket
import ssl


class SecureJSONRPCRequestHandler(
        SimpleJSONRPCServer.SimpleJSONRPCRequestHandler):
    """Secure JSON-RPC Request handler class

    Idea copied from http://code.activestate.com/recipes/496786/ but made
    to work with JSON-RPC instead of XML-RPC
    """
    def setup(self):
        """Setup the connection."""
        self.connection = self.request
        self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
        self.wfile = socket._fileobject(self.request, "wb", self.wbufsize)


class SecureJSONRPCServer(BaseHTTPServer.HTTPServer,
        SimpleJSONRPCServer.SimpleJSONRPCDispatcher):
    """Secure JSON-RPC server.
    Idea copied from http://code.activestate.com/recipes/496786/ but made
    to work with JSON-RPC instead of XML-RPC
    """
    def __init__(self, addr, requestHandler=SecureJSONRPCRequestHandler,
            logRequests=True, certFile=None, keyFile=None,
            cert_reqs=ssl.CERT_NONE, ssl_protocol=ssl.PROTOCOL_SSLv23):
        """Initialize this class and its base classes."""
        self.logRequests = logRequests

        SimpleJSONRPCServer.SimpleJSONRPCDispatcher.__init__(self)
        SocketServer.BaseServer.__init__(self, addr, requestHandler)

        # Test1
        #from OpenSSL import SSL
        #ctx = SSL.Context(SSL.SSLv23_METHOD)
        #key = 'certs/nfquery.key'
        #cert = 'certs/nfquery.crt'
        #ctx.use_privatekey_file(key)
        #ctx.use_certificate_file(cert)
        #self.socket = SSL.Connection(ctx, socket.socket(self.address_family,
        #                                                        self.socket_type))
        ##if bind_and_activate:
        #self.server_bind()
        #self.server_activate()

        # Test2
        sock = socket.socket(self.address_family, self.socket_type)
        
        self.socket = ssl.wrap_socket(sock,
                certfile=certFile,
                cert_reqs=cert_reqs,
                ca_certs=keyFile,
                ssl_version=ssl_protocol)

        self.server_bind()
        self.server_activate()

    def do_POST(self):
        """Handle a POST."""
        SimpleJSONRPCRequestHandler.do_POST(self)
        self.connection.shutdown(0)


if __name__ == '__main__':
    print 'Running Secure JSON-RPC server on port 8000'
    server = SecureJSONRPCServer(("localhost", 8000), keyFile='certs/nfquery.key', certFile='certs/nfquery.crt')
    server.register_function(pow)
    server.register_function(lambda x,y: x+y, 'add')
    server.serve_forever()


