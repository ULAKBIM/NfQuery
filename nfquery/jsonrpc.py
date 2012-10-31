# This file is part of NfQuery.  NfQuery is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright NfQuery Team Members

#!/usr/local/bin/python


import sys
import hashlib
import time

from txjsonrpc.web import jsonrpc
from twisted.web import server
from twisted.internet import reactor, ssl
from twisted.application import service,internet

import db
from models import Plugin, Prefix, Alert
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

    def jsonrpc_push_alerts(self, plugin_ip, query_id_list, start_time, end_time):
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.queryManager.pushAlerts(plugin_ip, query_id_list, start_time, end_time)

    def jsonrpc_register(self,plugin_ip):
        result = []
        print plugin_ip
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        # DEBUG mode da hangi fieldlarin hatali geldigini yazdirabiliriz tabiki sadece query server ' a.
        self.store = db.get_store()
        plugin = self.store.find(Plugin, Plugin.plugin_ip == plugin_ip).one()
        #TODO Anywhere plugins registered flags not set. Flags must be define.
        if plugin is None:
            result.append(0);
            print result
            return result
        else:
            if plugin.registered == 1:
                result.append(1)
                print result
                return result
            if plugin.registered == 2:
                result.append(2)
                print result
                return result
            if plugin.registered == 3:
                result.append(3)
                print result
                return result
        print result
        return result
#    print organization
#    print prefix_list
#    print plugin_ip
#    print adm_publickey_file
#    print adm_tel
#    print adm_name
#    print adm_mail
#        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
#        # DEBUG mode da hangi fieldlarin hatali geldigini yazdirabiliriz tabiki sadece query server ' a.
#        #print "Registration information : %s,%s,%s,%s,%s,%s,%s" % (organization, adm_name, adm_mail, adm_tel, adm_publickey, prefix_list, plugin_ip)
#        self.store = db.get_store()
#        plugin = self.store.find(Plugin, Plugin.organization == unicode(organization)).one()
#        if plugin is None:
#            message =  'Your plugin is not registered to QueryServer yet.'
#            message += 'Plugin is not found.'
#            message += 'Please ask to QS Administrator about your registration process.'
#            self.rpclogger.info("AAAAAAAAAAa")
#            print message
#        result.append(0)
#        print result
#            return result
#        else:
#            checksum = hashlib.md5()
#            checksum.update( organization + adm_name + adm_mail + 
#                             adm_tel      + adm_publickey_file  + 
#                             prefix_list  + plugin_ip )
#            if checksum.hexdigest() != plugin.checksum:
#                message = 'Your plugin information doesn\'t match with the QueryServer side.'
#                message += 'Plugin Checksum Error'
#                message += 'Please check your information and try again.'
#            result.append(1)
#            print result
#                return result
#               # print message
#            elif checksum.hexdigest() == plugin.checksum:
#                # Set the plugin registered
#                plugin.registered = True
#                self.store.add(plugin)
#                self.store.commit()
#                message =  'Your plugin is registered.\n'
#                message += 'Feel free to checkout query subscriptions.'
#                #print message
#            result.append(2)
#            print result
#                return result
#                #return self.jsonrpc_get_subscriptions()

    def jsonrpc_get_query_filter(self,query_id):
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.rpclogger.debug('returning query filter')
        return self.queryManager.getFilter(query_id)


    def jsonrpc_get_subscription_detail(self, subscription):
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.rpclogger.debug('returning subscriptions detail')
        return self.queryManager.getSubscription(subscription)
    
    def jsonrpc_get_subscriptions(self):
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.rpclogger.debug('returning subscriptions')
        subs = self.queryManager.getAllSubscriptions()
        return list(subs)

    
    def jsonrpc_get_subscription(self, name):
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.rpclogger.debug('getting subscription information')
        return self.queryManager.getSubscription(name)


    def jsonrpc_get_prefixes(self, ip_address):
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.rpclogger.debug('getting prefix list information')
        plugin = self.store.find( Plugin, 
                                     Plugin.plugin_ip == unicode(ip_address)
                                   ).one()
        if not plugin:
            self.rpclogger.warning('Plugin ip is not correct')
            self.rpclogger.warning('Can not return prefix list')
            return
        else:
             p_list = {}
             p_list[plugin.id] = plugin.prefix.prefix
             return p_list


    def jsonrpc_get_alert(self, alert):
        print '\n'
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        result = self.queryManager.registerAlert(alert)
        return result

    def jsonrpc_get_my_alerts(self, plugin_ip):
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        alert_list = ''
        try:
            plugin_id = self.store.find( Plugin.id,
                                         Plugin.plugin_ip == unicode(plugin_ip)
                                       ).one()
            print plugin_id
            alert_list = self.store.find( Alert,
                                          Alert.plugin_id == plugin_id )
            print list(alert_list)
            self.rpclogger.debug('Returning alert list')
        except Exception, e:
            print e
            return
        #print list(alert_list)
        return list(alert_list)
        
        

 
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


