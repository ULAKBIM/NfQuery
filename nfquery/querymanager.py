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

import simplejson as json
import logging
import sys
import os.path
import hashlib
import subprocess
import time
import pprint
from datetime import datetime
# nfquery imports
import db
import logger
from models import *
from storm.locals import In
from utils import *
from querygenerator import QueryGenerator

__all__ = ['QueryManager']

class QueryManager:

    def __init__(self, sources=None, plugins=None):
        self.qmlogger = logger.createLogger('querymanager')
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.qmlogger.info('Starting QueryManager')
        self.store = db.get_store()
        self.sources = sources
        self.plugins = plugins
        self.QGenerator = QueryGenerator(sources)
        

    def start(self):
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.checkParsers()
        self.executeParsers()
        self.createSubscriptionPackets()

    ###########################################################
    ### Plugin Management                                   ###
    ###########################################################
    def reconfigurePlugins(self):
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.qmlogger.info('Reconfiguring plugins')

        dbplugins = self.store.find(Plugin)
        
        # Maintain the table for delete operations
        if not dbplugins.is_empty():
            plugins_list = []
            for index in range(len(self.plugins)):
                plugins_list.append(self.plugins[index].organization)
            for plugin in dbplugins:
                if not plugin.organization in(plugins_list):
                    self.qmlogger.warning( 'I will delete the plugin, '
                                           'Do you approve the deletion of '
                                           'plugin : %s', plugin.organization )
                    flag = ask_yes_no('', default="no")
                    if flag is True:
                        plugin_name = plugin.organization
                        prefix_id = plugin.prefix_id
                        self.store.find( Plugin, 
                                         Plugin.organization == plugin.organization
                                       ).remove()
                        self.store.find( Prefix, 
                                         Prefix.id == prefix_id ).remove()
                        self.store.commit()
                        self.qmlogger.warning( 'Plugin %s is deleted' % 
                                               plugin_name )
                    else:
                        self.qmlogger.info('Not deleted anything.')
        
        for index in range(len(self.plugins)):
            # Calculate the checksum
            conf_checksum = hashlib.md5()
            #print self.plugins[index].organization,\
            #      self.plugins[index].adm_name, \
            #      self.plugins[index].adm_mail, \
            #      self.plugins[index].adm_tel, \
            #      self.plugins[index].adm_publickey_file, \
            #      self.plugins[index].prefix_list, \
            #      self.plugins[index].plugin_ip
            conf_checksum.update( str(self.plugins[index].organization)       +
                                  str(self.plugins[index].adm_name)           +
                                  str(self.plugins[index].adm_mail)           +
                                  str(self.plugins[index].adm_tel)            +
                                  str(self.plugins[index].adm_publickey_file) +
                                  str(self.plugins[index].prefix_list)        +
                                  str(self.plugins[index].plugin_ip) )
            #print conf_checksum.hexdigest()
            plugin_checksum = self.store.find( Plugin.checksum, 
                                               Plugin.organization == unicode( 
                                               self.plugins[index].organization)
                                             ).one()
            if plugin_checksum is None:
                self.qmlogger.info( 'Adding new plugin : "%s"' % 
                                    self.plugins[index].organization )
                plugin = Plugin()
                prefix_list = Prefix()
                prefix_list.prefix   = unicode(self.plugins[index].prefix_list)
                self.store.add(prefix_list)
                self.store.flush()
                plugin.organization = unicode(self.plugins[index].organization)
                plugin.adm_name = unicode(self.plugins[index].adm_name)
                plugin.adm_mail = unicode(self.plugins[index].adm_mail)
                plugin.adm_tel = unicode(self.plugins[index].adm_tel)
                plugin.adm_publickey_file = unicode(self.plugins[index].adm_publickey_file)
                plugin.plugin_ip = unicode(self.plugins[index].plugin_ip)
                plugin.prefix_id = prefix_list.id
                plugin.checksum = unicode(conf_checksum.hexdigest())
                self.store.add(plugin)
                self.store.commit()
                self.qmlogger.debug(plugin.id)
                self.qmlogger.debug(prefix_list.id)
                self.qmlogger.info( 'New Plugin added successfully : "%s"' % 
                                    self.plugins[index].organization )
            elif plugin_checksum == conf_checksum.hexdigest():
                self.qmlogger.info( 'No need to update the plugin : %s' % 
                                    self.plugins[index].organization )
            elif plugin_checksum != conf_checksum.hexdigest():
                # Update plugin information
                self.qmlogger.info( 'Updating the plugin %s' % 
                                    self.plugins[index].organization )
                # Update existing plugin information
                plugin = self.store.find( Plugin, 
                                          Plugin.organization == unicode( 
                                            self.plugins[index].organization) 
                                        ).one()
                plugin.organization = unicode(self.plugins[index].organization)
                plugin.adm_name = unicode(self.plugins[index].adm_name)
                plugin.adm_mail = unicode(self.plugins[index].adm_mail)
                plugin.adm_tel = unicode(self.plugins[index].adm_tel)
                plugin.adm_publickey_file = unicode(
                                         self.plugins[index].adm_publickey_file)
                plugin.plugin_ip = unicode(self.plugins[index].plugin_ip)
                plugin.checksum = unicode(conf_checksum.hexdigest())
                self.store.add(plugin)
                # Update existing prefix list information
                prefix_list = self.store.find( Prefix, 
                                               Prefix.id == plugin.prefix_id 
                                             ).one()
                prefix_list.prefix  = unicode(self.plugins[index].prefix_list)
                self.store.add(prefix_list)
                # Commit changes
                self.store.commit()
                self.qmlogger.info( 'Plugin updated successfully : "%s"' % 
                                    self.plugins[index].organization )
            else:
                self.qmlogger.error('CHECK CODE')
                self.qmlogger.warning('conf checksum ' + conf_checksum.hexdigest())
                self.qmlogger.warning('plugin_checksum ' + plugin_checksum)
        sys.exit()


    ###########################################################
    ### Source Management                                   ###
    ###########################################################
    def reconfigureSources(self):
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.qmlogger.info('Reconfiguring sources')

        # Check lists, tihs will handled in db creation later.
        threat = self.store.find(Threat)
        if threat.is_empty():
            db.insert_threats(self.store)

        dbsources = self.store.find(Source)
        # Maintain the table for delete operations
        if not dbsources.is_empty():
            sources_list = []
            for index in range(len(self.sources)):
                sources_list.append(self.sources[index].source_name)
            for source in dbsources:
                if not source.name in(sources_list):
                    self.qmlogger.warning(
                        ( "I will delete the source, Do you approve the deleti"
                          "on of source '%s' and queries generated from this s"
                          "ource '%s'"), 
                          source.name, source.name 
                        )
                    flag = ask_yes_no('', default="no")
                    if flag is True:
                        source_name = source.name
                        threat_id = source.threat_id
                        parser_id = source.parser_id
                       # subscription = self.store.find(Subscription, Subscription.name == source_name).one()
                       # self.store.find(SubscriptionPacket, SubscriptionPacket.subscription_id == subscription.id).remove()
                       # self.store.find(Subscription, Subscription.name == source_name).remove()
                      
                        source = self.store.find( Source,
                                            Source.name == source.name
                                           ).one()
                        source.is_active = 0
                       # source = self.store.find( Source, 
                       #                  Source.name == source.name 
                       #                ).remove()
                       # self.store.find( Parser, 
                       #                  Parser.id == parser_id 
                       #                ).remove()
                        self.store.commit()
                        self.qmlogger.warning( 'Source %s is deleted' % 
                                               source_name )
                    else:
                        self.qmlogger.info('Not deleted any source.')
                    
        dbsubscriptions = self.store.find(Subscription.name, Subscription.type == 1)
        if not dbsubscriptions.count() == 0:
            subscription_list = []
            for subs in dbsubscriptions:
                subscription_list.append(subs)
            print subscription_list
            for subscription_name in dbsubscriptions:
                if not subscription_name in(sources_list):
                    self.qmlogger.info('Do you want delete subscription %s from QS' %subscription_name)
                    flag = ask_yes_no('', default="no")
                    if flag is True:
                        subscription_id = self.store.find(Subscription.id, Subscription.name == subscription_name).one()
                         
                        self.store.find(SubscriptionPacket, SubscriptionPacket.subscription_id == subscription_id).remove()
                        self.store.find(Subscription, Subscription.name == subscription_name).remove()
                        self.store.commit()
                        self.qmlogger.warning( 'Subscription %s is deleted' % 
                                                  subscription_name )
                    else:
                        self.qmlogger.info('Not deleted any subscription.')
                        
        for index in range(len(self.sources)):
            # Check list type
            threat_id = self.store.find( Threat.id, 
                                         Threat.type == unicode(
                                         self.sources[index].threat_type)
                                       ).one()
            if threat_id is None:
                self.qmlogger.warning('Threat type couldn\'t be found'
                                      ' in the database, please check'
                                      ' your configuration.')
                self.qmlogger.warning('Assigning default list type value.')
                threat_id = 1 #means default unknown list type

            # Calculate the checksum
            conf_checksum = hashlib.md5()   
            conf_checksum.update(self.sources[index].source_name        +
                                 str(self.sources[index].threat_type)   + 
                                 self.sources[index].source_link        + 
                                 self.sources[index].source_file        +
                                 self.sources[index].parser             + 
                                 str(self.sources[index].time_interval) )
            source_checksum = self.store.find( Source.checksum, 
                                               Source.name == unicode(
                                               self.sources[index].source_name)
                                             ).one()
            if source_checksum is None:
                # Adding new source
                self.qmlogger.info( 'Adding new source %s' % 
                                    self.sources[index].source_name )
                # Add new parser
                parser = Parser()
                parser.name = unicode(self.sources[index].parser)
                parser.time_interval = self.sources[index].time_interval 
                self.store.add(parser)
                self.store.flush()
                # Add new source
                source = Source()
                source.name = unicode(self.sources[index].source_name)
                source.link = unicode(self.sources[index].source_link)
                source.threat_id = threat_id
                source.parser_id = parser.id
                source.is_active = 1
                source.checksum = unicode(conf_checksum.hexdigest())
                self.store.add(source)
                # Commit changes
                self.store.commit()
                self.qmlogger.info( 'New Source added successfully : "%s"' % 
                                    self.sources[index].source_name )
            elif str(conf_checksum.hexdigest()) == str(source_checksum):
                self.qmlogger.info( 'No need to reconfigure the source : %s' % 
                                    self.sources[index].source_name )
            elif str(conf_checksum.hexdigest()) != str(source_checksum):
                # Update source information
                self.qmlogger.info( 'Updating the source %s' % 
                                    self.sources[index].source_name )
                # Update existing source
                source = self.store.find( Source, Source.name == '%s' % unicode(
                                          self.sources[index].source_name) 
                                        ).one()
                source.link = unicode(self.sources[index].source_link)
                source.threat_id = threat_id
                source.checksum = unicode(conf_checksum.hexdigest())
                self.store.add(source)
                # Update existing parser
                parser = self.store.find( Parser, 
                                          Parser.id == source.parser_id
                                        ).one()
                parser.name = unicode(self.sources[index].parser)
                parser.time_interval = self.sources[index].time_interval
                self.store.add(parser)
                # Commit changes
                self.store.commit()
                self.qmlogger.info( 'Source updated successfully : "%s"' % 
                                    self.sources[index].source_name )
            else:
                self.qmlogger.error('CHECK CODE')
                self.qmlogger.warning('conf checksum ' + conf_checksum.hexdigest())
                self.qmlogger.warning('source_checksum ' + source_checksum)
                sys.exit()
        # reconfigure subscription types 
        self.createSubscriptionTypes()
        sys.exit()


    ###########################################################
    ### Parser Management                                   ###
    ###########################################################
    def checkParsers(self):
        '''
            Check if the parser exists in the given path.
        '''
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        for index in range(len(self.sources)):
            if os.path.exists(self.sources[index].parser):
                self.qmlogger.info( 'Parser "%s" exists, OK!' % 
                                    self.sources[index].parser )
            else:
                self.qmlogger.warning('Parser doesn\'t exist : %s' % self.sources[index].parser)
                self.qmlogger.warning( 'Please check your configuration file')
                print self.sources[index].parser
                # TODO : Create a list of found parsers and execute only this list
                # in executeParsers ;), because executeParser gives error if it can't
                # find a parser and crash!!!

    
    def executeParsers(self, parser=None):
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        if parser is None:
            self.qmlogger.debug('running all parsers')
            for index in range(len(self.sources)):
                try:
                    self.qmlogger.info('Running parser : %s' % self.sources[index].parser)
                    returncode = subprocess.call([ 'python', 
                                                   self.sources[index].parser] )
                    if returncode == 0:
                        self.QGenerator.createQuery(self.sources[index].parser)
                    else:
                        self.qmlogger.warning('Parser returned with error')
                    #self.QGenerator.createQuery(self.sources[index].parser)
                except Exception, e:
                    self.qmlogger.error('got exception: %r, exiting' % (e))
                    continue
        else:
            self.qmlogger.debug('running parser %s' % parser)
            for index in range(len(self.sources)):
                if self.sources[index].parser == parser:
                    try:
                        self.qmlogger.info('Running parser : %s' % self.sources[index].parser)
                        returncode = subprocess.call([ 'python', 
                                                       self.sources[index].parser])
                        if returncode == 0:
                            self.QGenerator.createQuery(self.sources[index].parser)
                        else:
                            self.qmlogger.warning('Parser returned with error')
                    except Exception, e:
                        self.qmlogger.error('got exception: %r, exiting' % (e))
                        continue


    ###########################################################
    ###  == Subscription Management ==                      ###
    ###########################################################
    
    # Subscription Types Creation 
    def createSubscriptionTypes(self):
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        '''
            We have 2 different subscription types.
            
            1) Source -> example : "Amada,Malc0de,DFN-Honeypot,
                                    ABC-NREN_Special_Source"
            2) Threat Type -> example : "Botnet,Malware,Honeypot Output, 
                                         Special Source Output"
            
            !!!!!! SUBSCRIPTION_TAGS NE OLACAK !!!!!!!!
    
        '''
    
        # 1) Source Name
        subscription_type=1
        source_name_list = self.store.find(Source.name, Source.is_active == 1)
        source_name_list.group_by(Source.name)
        for source_name in source_name_list:
            subscription = self.store.find( Subscription.id, 
                                            Subscription.name == '%s' % 
                                            (source_name) )
            
            if subscription.is_empty():
                subscription = Subscription()
                subscription.type = subscription_type
                subscription.name = source_name
                self.store.add(subscription)
                self.qmlogger.debug( 'Subscription type %s added to db' % 
                                     source_name )
    
        # 2) Threat Type
        subscription_type=2
        threat_type_list = self.store.find(Threat.type)
        threat_type_list.group_by(Threat.type)
        for threat_type in threat_type_list:
            subscription = self.store.find( Subscription.id, 
                                            Subscription.name == '%s' % 
                                            (threat_type)
                                          )
            if subscription.is_empty():
                subscription = Subscription()
                subscription.type = subscription_type
                subscription.name = threat_type
                self.store.add(subscription)
                self.qmlogger.debug( 'Subscription type %s added to db' % 
                                     threat_type )

        self.store.commit()
        self.qmlogger.debug('Subscription types are created')

    
    ###########################################################
    ### Subscription Packets Creation                       ###
    ###########################################################
    def createSubscriptionPackets(self):
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.qmlogger.info('Generating Subscriptions...')
        self.createSourceSubscriptionPackets()
        self.createThreatSubscriptionPackets()
    
    
    def createSourceSubscriptionPackets(self):
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        # If source_name is not given, we work for all sources.
        subs_list = self.store.find(( Subscription.id, Subscription.name),
                                      (Subscription.type == 1) &
                                      (Subscription.name == Source.name)   )
        for subs_id, subs_name in subs_list:
            s_id = self.store.find( Source.id, 
                                    Source.name == subs_name ).one()
            query_id_list = self.store.find( Query.id,
                                            (Query.category_id == 1) &
                                            (Query.source_id == s_id)  )
            for q_id in query_id_list:
                qp_id = self.store.find( QueryPacket.id,
                                         QueryPacket.query_id == q_id ).one()
                if qp_id:
                    # Check if it exists already
                    s_packet = self.store.find( SubscriptionPacket.id,
                                                (SubscriptionPacket.subscription_id == subs_id) & 
                                                (SubscriptionPacket.query_packet_id == qp_id) ).one()
                    if not s_packet:
                        spacket = SubscriptionPacket()
                        spacket.subscription_id = subs_id
                        spacket.query_packet_id = qp_id
                        self.store.add(spacket)
                        self.store.flush()
                        #self.store.commit()
                    else:
                        #self.qmlogger.debug('subscription packet already generated.')
                        pass
                else:
                    raise Exception, 'QueryPacket couldn\'t be empty'
        self.store.commit()


    def createThreatSubscriptionPackets(self):
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        # If source_name is not given, we work for all sources.
        subs_list = self.store.find( (Subscription.id, Subscription.name),
                                     (Subscription.type == 2) &
                                     (Subscription.name == Threat.type)   ) 
        for subs_id, subs_name in subs_list:
            t_id = self.store.find( Threat.id,
                                    Threat.type == subs_name).one()
            source_id_list = self.store.find( Source.id, 
                                              Source.threat_id == t_id )
            for s_id in source_id_list:
                query_id_list = self.store.find( Query.id,
                                                 (Query.category_id ==1) & 
                                                 (Query.source_id == s_id)   )
                for q_id in query_id_list:
                    qp_id = self.store.find( QueryPacket.id,
                                             QueryPacket.query_id == q_id ).one()
                    if qp_id:
                        # Check if it exists already
                        s_packet = self.store.find( SubscriptionPacket.id,
                                                    (SubscriptionPacket.subscription_id == subs_id) &
                                                    (SubscriptionPacket.query_packet_id == qp_id)     )
                        if s_packet.is_empty():
                            spacket  = SubscriptionPacket()
                            spacket.subscription_id = subs_id
                            spacket.query_packet_id = qp_id
                            self.store.add(spacket)
                            self.store.flush()
                        else:
                            #self.qmlogger.debug('subscription packet already generated.')
                            pass
                    else:
                        raise Exception, 'QueryPacket couldn\'t be empty'
        self.store.commit()
	



    def getFilter(self, query_id):
	query_id = int(query_id)
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        pp = pprint.PrettyPrinter(indent=4)
        self.qmlogger.debug('Getting filter, query_id %d' % query_id)
        query = self.store.find(Query, Query.id == query_id).one()
        query_filter = self.QGenerator.createQueryFilter([query])
	return query_filter

   


 
    ###########################################################
    ### Subscription Releasing and Plugin Request Handling  ###
    ###########################################################
    def getSubscription(self, name):
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.qmlogger.debug('subscription_name = %s' % name)
        pp = pprint.PrettyPrinter(indent=4)
        self.qmlogger.debug('Getting subscription %s' % name)
        subscription_id = self.store.find(Subscription.id, Subscription.name == unicode(name)).one()
        self.qmlogger.debug('subscription_id = %d' % subscription_id)
        if subscription_id:
            self.qmlogger.debug('y1')
            qpacket_list = self.store.find(SubscriptionPacket.query_packet_id, SubscriptionPacket.subscription_id == subscription_id)
            if not qpacket_list.is_empty():
                result = {}
                self.qmlogger.debug('y2')
                qp_query_id_list = self.store.find(QueryPacket.query_id, In(QueryPacket.id, list(qpacket_list)))
                query_packet = {}
                for qp_query_id in qp_query_id_list:
                    # I've validation id, now let's get other ids and try to create the whole query_packet
                    query_packet_ids = self.store.find(QueryPacket.query_id, QueryPacket.validation_id == qp_query_id)
                    packet = {}
                    index = 0
                    for query_id in query_packet_ids:
                        query = self.store.find(Query, Query.id == query_id).one()
                        query_filter = self.QGenerator.createQueryFilter([query])
                        if query.category_id == 1:
                            query_packet_id = query.id
                        query_type = self.store.find(Type.type, query.type_id == Type.id).one()
                        source = self.store.find(Source, Source.id == query.source_id).one()
		        category = self.store.find(Category,Category.id == query.category_id).one()	
                        #print query_type
                        packet[index] = {   
                                         'query_id' : query.id, 
                                         'query_type' : query_type,
                                         'category_id' : query.category_id,
                                         'filter' : query_filter,
                                         'category_name' : category.category,
                                         'source_name' : source.name,
                                         'link' : source.link
                                        }
                        index += 1
                    query_packet[qp_query_id] = packet
                result[subscription_id] = query_packet
                self.qmlogger.debug('Returning details for subscription %s ' % name)
                return result
        self.qmlogger.warning('Couldn\'t get details for subscription %s ' % name)
        return


    def getAllSubscriptions(self):
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        subscription_list = self.store.find((Subscription.id, Subscription.name))
        self.qmlogger.debug('Returning subscription list')
        return dict(subscription_list)  

    def getStatistics(self, alert_id):
        statistic = self.store.find(Statistics, Statistics.alert_id == int(alert_id)).one()
        statistics = {}
        statistics["alert_id"] = int(statistic.alert_id)
        statistics["number_of_flows"] = statistic.number_of_flows
        statistics["number_of_bytes"] = statistic.number_of_bytes
        statistics["number_of_packets"] = statistic.number_of_packets
        return statistics
    
    def getTopNQuery(self, n):
        result = self.store.find((Alert, Count(Alert.query_id))).group_by(Alert.query_id).order_by(Desc(Count(Alert.query_id))).config(limit=int(n))

        topN_list = []

        for alert, count in result:
            item = {}
            item['query_id'] = alert.query_id
            item['query'] = self.getFilter(alert.query_id)
            item['query_category'] = alert.query.category.category
            item['count'] = count
            item['source_name'] = alert.query.source.name

            #Append item to topNlist
            topN_list.append(item)
        
        return topN_list

    def getMyAlerts(self, plugin_ip):
        plugin_id = self.store.find( Plugin.id,Plugin.plugin_ip == unicode(plugin_ip)).one()
        print plugin_id

        alerts = {}
        alert_list = ''

        #Identifier
        alert_list = self.store.find( Alert, Alert.identifier_plugin_id == plugin_id )
        alerts['identifier'] = []
        for alert in alert_list:
            identifier = {}
            identifier['alert_id'] = alert.id
            identifier["identified_plugin_name"] = alert.identified_plugin.organization
            identifier["identifier_plugin_name"] = alert.identifier_plugin.organization
            identifier["identified_plugin_id"] = alert.identified_plugin.id
            identifier["identifier_plugin_id"] = alert.identifier_plugin.id
            identifier["first_seen"] = alert.first_seen
            identifier["checksum"] = alert.checksum
            identifier["query_id"] = alert.query.id
            identifier["start_time"] = alert.start_time
            identifier["end_time"] = alert.end_time
            identifier["query_category"] = alert.query.category.category
            identifier["query_filter"] = self.getFilter(alert.query.id)
            identifier["statistic"] = self.getStatistics(alert.id)
            
            alerts['identifier'].append(identifier)
        print list(alert_list)

        #Identified
        alert_list = self.store.find( Alert, Alert.identified_plugin_id == plugin_id, Alert.identifier_plugin_id != Alert.identified_plugin_id )
        alerts['identified'] = []
        for alert in alert_list:
            identified = {}
            identified['alert_id'] = alert.id
            identified["identified_plugin_name"] = alert.identified_plugin.organization
            identified["identifier_plugin_name"] = alert.identifier_plugin.organization
            identified["identified_plugin_id"] = alert.identified_plugin.id
            identified["identifier_plugin_id"] = alert.identifier_plugin.id
            identified["first_seen"] = alert.first_seen
            identified["checksum"] = alert.checksum
            identified["query_id"] = alert.query.id
            identified["start_time"] = alert.start_time
            identified["end_time"] = alert.end_time
            identified["query_category"] = alert.query.category.category
            identified["query_filter"] = self.getFilter(alert.query.id)
            identified["statistic"] = self.getStatistics(alert.id)
            alerts['identified'].append(identified)
        print list(alerts)


        return alerts


    def insertAlert(self, alert_info):
       alert = Alert()
       alert.identified_plugin_id = alert_info['identified_plugin_id']
       alert.identifier_plugin_id = alert_info['identifier_plugin_id']
       alert.start_time = alert_info["timewindow_start"]
       alert.end_time = alert_info["timewindow_end"]
       alert.first_seen = alert_info["timestamp"]
       alert.checksum = alert_info['checksum']
       alert.query_id = alert_info['query_id']
       self.store.add(alert)
       statistic = Statistics()
       statistic.start_time = alert_info["timewindow_start"]
       statistic.end_time = alert_info["timewindow_end"]
       statistic.number_of_flows = alert_info["flows"]
       statistic.number_of_packets = alert_info["bytes"]
       statistic.number_of_bytes = alert_info["packets"]
       statistic.query_id = alert_info['query_id']
       statistic.plugin_id = alert_info['plugin_id']
       statistic.alert = alert
       self.store.add(statistic)
       self.store.commit()

    def pushAlerts(self, plugin_ip, query_id_list, start_time, end_time):
        print query_id_list
        plugin_id = self.store.find( Plugin.id,Plugin.plugin_ip == unicode(plugin_ip)).one()
        for query_id, query_list in query_id_list.items():
            if query_list.has_key("alerts"):
                for hash_key, row_data in query_list["alerts"].items():
                    if 'srcip_alert_plugin' and 'dstip_alert_plugin' in row_data.keys():
                        plugin_id_list = [row_data['srcip_alert_plugin'],row_data['dstip_alert_plugin']]
                        for id in plugin_id_list:
                            alert = self.store.find( Alert,
                                Alert.checksum == hash_key, Alert.identifier_plugin_id == int(plugin_id),
                                Alert.identified_plugin_id == int(id),
                                Alert.query_id == int(query_id)).one()
                            
                            if alert is None:
                                alert_info = {'identifier_plugin_id' : plugin_id, 'identified_plugin_id' : int(id), 
                                              'timewindow_start' : int(start_time), 'timewindow_end' : int(end_time), 
                                              'timestamp' : row_data["timestamp"], 'checksum' : hash_key,
                                              'query_id' : int(query_id), 'flows' : int(row_data["flows"]), 'bytes': int(row_data["bytes"]),
                                              'packets' : int(row_data["packets"]), 'plugin_id': int(plugin_id)}
                                self.insertAlert(alert_info)        
              

                

    def registerAlert(self, alert):
        pp = pprint.PrettyPrinter(indent=4)
        print '\n'
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        #print '============= ALERT PACKET ==============='
        #pp.pprint(alert)
        #print '============= ALERT PACKET ==============='
        #print '\n'

        prefix = alert[0]["prefix"]
        del alert[0]["prefix"]
        prefix_id = self.store.find( Prefix.id, 
                                     Prefix.prefix == unicode(prefix) 
                                   ).one()
        plugin_id = self.store.find( Plugin.id,
                                     Plugin.prefix_id == prefix_id 
                                   ).one()
        #print 'plugin_id', plugin_id

        try:
            alert = self.QGenerator.validateAlert(alert)
            #pp.pprint(alert)
            self.qmlogger.info('Validated alert packet')
            alert_query_list = self.QGenerator.generateQuery(alert)
            #print alert_query_list
        except Exception, e:
            print e
            return
        
        # ayni query insert edilmeyeceginden, generateQuery ' den q_id donmez
        # o zaman alerti eklemeye de gerek kalmaz.
        if not alert_query_list:
            self.qmlogger.info('Alert is already created')
            #alerts = self.store.find( Alert.id,
            #                          Alert.query_id == q_id )
            print '\n'
            return 'Alert is already created.'
        else:
            alert_id_list = []
            alert_id = ''
            expression = 'select max(id) from alert'
            result = self.store.execute(expression)
            result = result.get_one()
            if result[0]:
                alert_id = int(result[0]) + 1 
            else:
                alert_id = 1
            for index in range(len((alert_query_list))):
                try:
                    alert = Alert()
                    alert.alert_id = alert_id
                    alert.query_id = alert_query_list[index]
                    alert.plugin_id = plugin_id
                    self.store.add(alert)
                    self.store.flush()
                    alert_id_list.append(alert_id)
                    self.store.commit()
                except Exception, e:
                    print e
                    return
            message = 'Created new alert, alert id : %d' %  alert_id
            self.qmlogger.warning(message)
            #print alert_id_list
            #self.qmlogger.warning('Returning alert list ')
            print '\n'
            return message
       

  
    def generateQuery(self, query_info_list, mandatory, plugin_ip):
        plugin = self.store.find( Plugin, Plugin.plugin_ip == unicode(plugin_ip)).one()
        current_time = datetime.today()
        date_string = current_time.strftime("%Y-%m-%d %H:%M")
        query_info = [{
                             'date':  date_string,
                             'expr_list' : [json.loads(query_info_list)],
                             'mandatory_keys': json.loads(mandatory),
                             'source_name': plugin.organization
                          }]
        source = self.store.find(Source, Source.name == unicode(query_info[0]['source_name'])).one()
        query_info[0]['source_id'] = source.id
        query_info[0]['date'] = datetime.strptime(query_info[0]['date'], '%Y-%m-%d %H:%M')
        self.QGenerator.generateQuery(query_info)
        return True 
        
