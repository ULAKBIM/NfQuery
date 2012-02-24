#!/usr/local/bin/python


#First One 

from twisted.internet import reactor
from txjsonrpc.web.jsonrpc import Proxy
import time

def printValue(value):
    print "Result: %s" % str(value)

def printError(error):
    print 'error', error

def shutDown(data):
    print "Shutting down reactor..."
    reactor.stop()

##proxy = Proxy('http://127.0.0.1:7080/')

proxy = Proxy('https://127.0.0.1:7777/')
#d = proxy.callRemote('add', 3, 5)
e = proxy.callRemote('register', "a", "b","c","d","e","f","g")
#d.addCallback(printValue).addErrback(printError).addBoth(shutDown)
e.addCallback(printValue).addErrback(printError).addBoth(shutDown)
#d.addCallback(printValue).addErrback(printError)
reactor.run()





#
#time.sleep(2)
#print 'woke up'

# Second One
#import jsonrpclib
#
#s = jsonrpclib.Server('https://127.0.0.1:7777/')
#while 1:
#    print s.add(1,2)
#    print s.echo('hellloooouuu')
#    time.sleep(10)

