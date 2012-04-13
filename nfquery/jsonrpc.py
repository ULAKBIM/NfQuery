#!/usr/local/bin/python


import sys
import hashlib
import time

from txjsonrpc.web import jsonrpc
from twisted.web import server
from twisted.internet import reactor, ssl
from twisted.application import service,internet

import db
from models import Plugin, Prefix 
from logger import createLogger

class jsonRPCServer(jsonrpc.JSONRPC):
    """
    An example object to be published.
    """

    def __init__(self, queryManager):
        self.rpclogger = createLogger('RPC')
        self.rpclogger.info('Starting JSONRPCServer')
        #self.queryGen = queryManager.queryGenerator
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


    def jsonrpc_register(self, organization, adm_name, adm_mail, adm_tel, adm_publickey_file, prefix_list, plugin_ip):
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
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
                return message
                #return self.jsonrpc_get_subscriptions()

    
    def jsonrpc_get_subscriptions(self):
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.rpclogger.debug('returning subscriptions')
        return list(self.queryManager.getAllSubscriptions())

    
    def jsonrpc_get_subscription(self, name):
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.rpclogger.debug('getting subscription information')
        return self.queryManager.getSubscription(name)


    def jsonrpc_get_prefixes(self, ip_address):
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.rpclogger.debug('getting prefix list information')
        prefix_id = self.store.find( Plugin.prefix_id, 
                                     Plugin.plugin_ip == unicode(ip_address)
                                   ).one()
        if not prefix_id:
            self.rpclogger.warning('Plugin ip is not correct')
            self.rpclogger.warning('Can not return prefix list')
            return
        else:
            prefix_list = self.store.find(Prefix.prefix)
            p_list = []
            for prefix in prefix_list:
                p_list.append(prefix)
            print p_list
            return p_list


    def jsonrpc_get_alert(self, alert):
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        result = self.queryManager.registerAlert(alert)
        return result
        
        
        


 
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


