#!/usr/local/bin/python


#First One 

from twisted.internet import reactor
from txjsonrpc.web.jsonrpc import Proxy

def printValue(value):
    print "Result: %s" % str(value)

def printError(error):
    print 'error', error

def shutDown(data):
    print "Shutting down reactor..."
    reactor.stop()

#proxy = Proxy('http://127.0.0.1:7080/')
proxy = Proxy('http://127.0.0.1:7777/')

d = proxy.callRemote('add', 3, 5)
d.addCallback(printValue).addErrback(printError).addBoth(shutDown)
#d.addCallback(printValue).addErrback(printError)
reactor.run()


# Second One
