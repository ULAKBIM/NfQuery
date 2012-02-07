#!/usr/local/bin/python


from txjsonrpc.web import jsonrpc
from twisted.web import server
from twisted.internet import reactor


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
        return a + b

    def jsonrpc_fault(self):
        """
        Raise a Fault indicating that the procedure should not be used.
        """
        raise jsonrpc.Fault(123, "The fault procedure is faulty.")

if __name__ == '__main__':
    r = Example()
    reactor.listenTCP(7080, server.Site(r))
    reactor.run()
    print 'a'
