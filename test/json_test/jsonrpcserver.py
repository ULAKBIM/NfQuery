#!/usr/local/bin/python

import SocketServer


class ThreadingTCPRequestHandler(SocketServer.BaseRequestHandler):
    '''
        The RequestHandler class for our server.

        It is instantiated once per connection to the server, and must
        override the handle() method to implement communication to the
        client.
    '''
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "%s wrote:" % self.client_address[0]
        print self.data
        # just send back the same data, but upper-cased
        self.request.send(self.data.upper())

#class ThreadingTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
#    daemon_threads=True
#    allow_reuse_address=True
#    def __init__(self, server_address, RequestHandlerClass):
#        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)
#        print 'used'
#        # start logging
#        logging.setLoggerClass(ColoredLogger)
#        self.slogger = logging.getLogger('ThreadingTCPServer')
#        self.slogger.setLevel(defaults.loglevel)
#        self.slogger.info('Server is initiated')
# -------------------------------------------------------------------------------------#
