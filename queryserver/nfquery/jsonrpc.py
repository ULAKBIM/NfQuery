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

import sys
import hashlib

from txjsonrpc.web import jsonrpc
from twisted.web import server
from twisted.internet import reactor, ssl
from twisted.application import service,internet

from models import Plugin, Prefix, Alert
from logger import createLogger
from querymanager import QueryManager

class jsonRPCServer(jsonrpc.JSONRPC):
    """
    An example object to be published.
    """

    def __init__(self, queryServer = None):
        ##ugur
        self.rpclogger = createLogger('RPC')
        self.rpclogger.info('Starting JSONRPCServer')
        self.queryServer = queryServer
        self.queryManager = QueryManager(store=self.queryServer.createStore(), sources=self.queryServer.config.sources, plugins=self.queryServer.config.plugins)

    def render(self, request):
        # check if db connection is lost or not!
        self.queryManager.setStore(self.queryServer.dbEnsureConnected(self.queryManager.store))
        return (jsonrpc.JSONRPC.render(self, request))

    def jsonrpc_push_alerts(self, plugin_ip, query_id_list, start_time, end_time):
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.queryManager.pushAlerts(plugin_ip, query_id_list, start_time, end_time)

    def jsonrpc_push_statistics(self, plugin_id, query_id, number_of_flows, number_of_bytes, number_of_packets, time_window):
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.queryManager.pushStatistics(plugin_ip, query_id_list, start_time, end_time)

    def jsonrpc_register(self,plugin_ip):
        result = []
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        # DEBUG mode da hangi fieldlarin hatali geldigini yazdirabiliriz tabiki sadece query server ' a.
        plugin = self.queryManager.store.find(Plugin, Plugin.plugin_ip == plugin_ip).one()
        #TODO Anywhere plugins registered flags not set. Flags must be define.
        if plugin is None:
            result.append(0);
            return result
        else:
            if plugin.registered == 1:
                result.append(1)
                return result
            if plugin.registered == 2:
                result.append(2)
                return result
            if plugin.registered == 3:
                result.append(3)
                return result
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

    def jsonrpc_get_statistics(self, alert_id):
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        result = self.queryManager.getStatistics(alert_id)
        return result

    def jsonrpc_get_topn_query(self, n):
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        result = self.queryManager.getTopNQuery(n)
        return result


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
        return subs


    def jsonrpc_get_subscription(self, name, method_call):
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.rpclogger.debug('getting subscription information')
        return self.queryManager.getSubscription(name, method_call)



    def jsonrpc_get_all_prefixes(self):
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.rpclogger.debug('getting all prefix list information')
        plugin_list = self.queryManager.store.find(Plugin)
        prefix_list = {}
        for plugin in plugin_list:
            prefix_list[plugin.id] = plugin.prefix.prefix.replace(" ","").split(',')
        print prefix_list
        return prefix_list


    def jsonrpc_get_plugin_id(self, ip_address):
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.rpclogger.debug('getting plugin id of ip address')
        return self.queryManager.getPluginId(ip_address)

    def jsonrpc_get_prefixes(self, ip_address):
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.rpclogger.debug('getting prefix list information')
        plugin = self.queryManager.store.find( Plugin,
                                     Plugin.plugin_ip == unicode(ip_address)
                                   ).one()
        if not plugin:
            self.rpclogger.warning('Plugin ip is not correct')
            self.rpclogger.warning('Can not return prefix list')
            return
        else:
             p_list = {}
             p_list[plugin.id] = plugin.prefix.prefix.replace(" ","").split(',')
             return p_list


    def jsonrpc_get_alert(self, alert):
        print '\n'
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        result = self.queryManager.registerAlert(alert)
        return result

    def jsonrpc_get_my_alerts(self, plugin_ip):
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        return self.queryManager.getMyAlerts(plugin_ip)

    def jsonrpc_generate_query(self, query_info_list, mandatory, plugin_ip):
        self.rpclogger.debug('In %s' % sys._getframe().f_code.co_name)
        return self.queryManager.generateQuery(query_info_list, mandatory, plugin_ip)

