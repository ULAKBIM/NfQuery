#!/usr/local/bin/python

import simplejson as json
import logging
import sys
import os.path
import hashlib
import subprocess
import time

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
            conf_checksum.update( self.plugins[index].organization       +
                                  self.plugins[index].adm_name           +
                                  self.plugins[index].adm_mail           +
                                  self.plugins[index].adm_tel            +
                                  self.plugins[index].adm_publickey_file +
                                  self.plugins[index].prefix_list        +
                                  self.plugins[index].plugin_ip )
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
            db.insertThreatTypes(self.store)

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
                        self.store.find( Source, 
                                         Source.name == source.name 
                                       ).remove()
                        self.store.find( Parser, 
                                         Parser.id == parser_id 
                                       ).remove()
                        self.store.commit()
                        self.qmlogger.warning( 'Source %s is deleted' % 
                                               source_name )
                    else:
                        self.qmlogger.info('Not deleted any source.')
                        
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
                self.qmlogger.warning('Parser %s doesn\'t exist')
                self.qmlogger.warning( 'Please check the nfquery.conf file' % 
                                       self.sources[index].parser )

    
    def executeParsers(self, parser=None):
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        if parser is None:
            self.qmlogger.debug('running all parsers')
            for index in range(len(self.sources)):
                try:
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
        source_name_list = self.store.find(Source.name)
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

    
    ###########################################################
    ### Subscription Releasing and Plugin Request Handling  ###
    ###########################################################
    def getSubscription(self, name):
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        import pprint
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
                        packet[index] = {   
                                         'query_id' : query.id, 
                                         'category_id' : query.category.id, 
                                         'filter' : query_filter
                                        }
                        index += 1
                    query_packet[qp_query_id] = packet
                result[subscription_id] = query_packet
                self.qmlogger.debug('Returning details for subscription %s ' % name)
                pp.pprint(result)
                return result
        self.qmlogger.warning('Couldn\'t get details for subscription %s ' % name)
        return


    def getAllSubscriptions(self):
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        subscription_list = self.store.find(Subscription.name)
        self.qmlogger.debug('Returning subscription list')
        #print list(subscription_list)
        return list(subscription_list)


            
