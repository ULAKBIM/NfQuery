#!/usr/local/bin/python


import sys
import hashlib
import time

from txjsonrpc.web import jsonrpc
from twisted.web import server
from twisted.internet import reactor, ssl
from twisted.application import service,internet

import db
from models import Plugin 
from logger import createLogger

class RPCServer(jsonrpc.JSONRPC):
    """
    An example object to be published.
    """

    def __init__(self, queryManager):
        self.rpclogger = createLogger('rpc')
        self.rpclogger.info('RPCServer is started')
        self.queryManager = queryManager

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

    
    def jsonrpc_get_subscriptions(self):
        return self.queryManager.getSubscriptions()


    def jsonrpc_register(self, organization, adm_name, adm_mail, adm_tel, adm_publickey_file, prefix_list, plugin_ip):
        # DEBUG mode da hangi fieldlarin hatali geldigini yazdirabiliriz tabiki sadece query server ' a.
        #print "Registration information : %s,%s,%s,%s,%s,%s,%s" % (organization, adm_name, adm_mail, adm_tel, adm_publickey, prefix_list, plugin_ip)
        self.store = db.get_store()
        plugin = self.store.find(Plugin, Plugin.organization == unicode(organization)).one()
        if plugin is None:
            message =  'Your plugin is not registered to QueryServer yet.'
            message += 'Plugin is not found.'
            message += 'Please ask to QS Administrator about your registration process.'
            print message
            return message
        else:
            checksum = hashlib.md5()
            checksum.update( organization + adm_name + adm_mail + adm_tel +
                             adm_publickey_file + prefix_list + plugin_ip  )
            if checksum.hexdigest() != plugin.checksum:
                message = 'Your plugin information doesn\'t match with the QueryServer side.'
                message += 'Plugin Checksum Error'
                message += 'Please check your information and try again.'
                print message
                return message 
            elif checksum.hexdigest() == plugin.checksum:
                # Set the plugin registered
                plugin.registered = True
                self.store.add(plugin)
                self.store.commit()
                message =  'Your plugin is registered.'
                message += 'Feel free to checkout query subscriptions.'
                print message
                return self.jsonrpc_get_subscriptions()
                #return self.queryServer.fetchSubscriptions()
                #return self.fetchSubscriptionTypes()
       

 
#def getExampleService():
#    r = Example()
#    exserver = server.Site(r)
#    return internet.TCPServer(7777,exserver, ssl.DefaultOpenSSLContextFactory('certs/nfquery.key', 'certs/nfquery.crt'))
#    #return internet.TCPServer(7777,exserver)

# ------------------------------------------------- # ------------------------------------------------ # ---------------------# 

#if __name__ == '__main__':
#    print dir(ssl.SSL)
#    sys.exit()
#    r = Example()
#    exserver = server.Site(r) 
#    #reactor.listenSSL(7777, exserver, ssl.DefaultOpenSSLContextFactory('certs/nfquery.key', 'certs/nfquery.crt'))
#    reactor.listenSSL(7777, exserver, ssl.DefaultOpenSSLContextFactory('/home/serdar/workspace/nfquery/cfg/certs/nfquery.key','/home/serdar/workspace/nfquery/cfg/certs/nfquery.crt'))
#    reactor.run()
#    print 'main'



#else:
#    application=service.Application('Example Application')
#    #service = reactor.listenSSL(7777, server.Site(r),ssl.DefaultOpenSSLContextFactory('certs/nfquery.key', 'certs/nfquery.crt'))
#    service = getExampleService()
#    service.setServiceParent(application)
#    print 'here'
#    #reactor.run()


