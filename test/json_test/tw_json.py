#!/usr/local/bin/python


from txjsonrpc.web import jsonrpc
from twisted.web import server
from twisted.internet import reactor, ssl
from twisted.application import service,internet


class Example(jsonrpc.JSONRPC):
    """
    An example object to be published.
    """

    def jsonrpc_echo(self, x):
        """
        Return all passed args.
        """
        return x

    def jsonrpc_add(self, a, b):
        """
        Return sum of arguments.
        """
        print a + b 
        return a + b

    def jsonrpc_fault(self):
        """
        Raise a Fault indicating that the procedure should not be used.
        """
        raise jsonrpc.Fault(123, "The fault procedure is faulty.")


def getExampleService():
    r = Example()
    exserver = server.Site(r)
    return internet.TCPServer(7777,exserver, ssl.DefaultOpenSSLContextFactory('certs/nfquery.key', 'certs/nfquery.crt'))
    #return internet.TCPServer(7777,exserver)

# ------------------------------------------------- # ------------------------------------------------ # ---------------------# 

#if __name__ == '__main__':
#    r = Example()
#    exserver = server.Site(r) 
#    reactor.listenSSL(7777, exserver, ssl.DefaultOpenSSLContextFactory('certs/nfquery.key', 'certs/nfquery.crt'))
#    reactor.run()
#    print 'main'
#else:
#    application=service.Application('Example Application')
#    #service = reactor.listenSSL(7777, server.Site(r),ssl.DefaultOpenSSLContextFactory('certs/nfquery.key', 'certs/nfquery.crt'))
#    service = getExampleService()
#    service.setServiceParent(application)
#    print 'here'
#    #reactor.run()


