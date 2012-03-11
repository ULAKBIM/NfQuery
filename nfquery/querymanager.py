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
        self.queryGenerator = QueryGenerator(sources)
        

    def start(self):
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.checkParsers()
        self.executeParsers()
        self.createSubscriptionPackets()

    # Plugin Management
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
                    self.qmlogger.warning('I will delete the plugin, Do you approve the deletion of plugin : %s',plugin.organization)
                    flag = query_yes_no('', default="no")
                    if flag is True:
                        plugin_name = plugin.organization
                        prefix_id = plugin.prefix_id
                        self.store.find(Plugin, Plugin.organization == plugin.organization).remove()
                        self.store.find(Prefix, Prefix.id == prefix_id).remove()
                        self.store.commit()
                        self.qmlogger.warning('Plugin %s is deleted' % plugin_name)
                    else:
                        self.qmlogger.info('Not deleted anything.')
        
        for index in range(len(self.plugins)):
            # Calculate the checksum
            conf_checksum = hashlib.md5()
            conf_checksum.update( self.plugins[index].organization       + self.plugins[index].adm_name    + 
                                  self.plugins[index].adm_mail           + self.plugins[index].adm_tel     +          
                                  self.plugins[index].adm_publickey_file + self.plugins[index].prefix_list +
                                  self.plugins[index].plugin_ip )
            plugin_checksum = self.store.find(Plugin.checksum, Plugin.organization == unicode(self.plugins[index].organization)).one()

            if plugin_checksum is None:
                self.qmlogger.info('Adding new plugin : "%s"' % self.plugins[index].organization)
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
                self.qmlogger.info('New Plugin added successfully : "%s"' % self.plugins[index].organization)
            elif plugin_checksum == conf_checksum.hexdigest():
                self.qmlogger.info('No need to update the plugin : %s' % self.plugins[index].organization)
            elif plugin_checksum != conf_checksum.hexdigest():
                # Update plugin information
                self.qmlogger.info('Updating the plugin %s' % self.plugins[index].organization)
                # Update existing plugin information
                plugin = self.store.find(Plugin, Plugin.organization == unicode(self.plugins[index].organization)).one()
                plugin.organization = unicode(self.plugins[index].organization)
                plugin.adm_name = unicode(self.plugins[index].adm_name)
                plugin.adm_mail = unicode(self.plugins[index].adm_mail)
                plugin.adm_tel = unicode(self.plugins[index].adm_tel)
                plugin.adm_publickey_file = unicode(self.plugins[index].adm_publickey_file)
                plugin.plugin_ip = unicode(self.plugins[index].plugin_ip)
                plugin.checksum = unicode(conf_checksum.hexdigest())
                self.store.add(plugin)
                # Update existing prefix list information
                prefix_list = self.store.find(Prefix, Prefix.id == plugin.prefix_id).one()
                prefix_list.prefix  = unicode(self.plugins[index].prefix_list)
                self.store.add(prefix_list)
                # Commit changes
                self.store.commit()
                self.qmlogger.info('Plugin updated successfully : "%s"' % self.plugins[index].organization)
            else:
                self.qmlogger.error('CHECK CODE')
                self.qmlogger.warning('conf checksum ' + conf_checksum.hexdigest())
                self.qmlogger.warning('plugin_checksum ' + plugin_checksum)
        sys.exit()


    # Source Management 
    def reconfigureSources(self):
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.qmlogger.info('Reconfiguring sources')

        # Check lists, tihs will handled in db creation later.
        list_obj = self.store.find(List)
        if list_obj.is_empty():
            db.insertListTypes(self.store)

        dbsources = self.store.find(Source)
        # Maintain the table for delete operations
        if not dbsources.is_empty():
            sources_list = []
            for index in range(len(self.sources)):
                sources_list.append(self.sources[index].sourcename)
            for source in dbsources:
                if not source.name in(sources_list):
                    self.qmlogger.warning('I will delete the source, Do you approve the deletion of source : %s', source.name)
                    flag = query_yes_no('', default="no")
                    if flag is True:
                        source_name = source.name
                        list_id = source.list_id
                        parser_id = source.parser_id
                        self.store.find(Source, Source.name == source.name).remove()
                        self.store.find(Parser, Parser.id == parser_id).remove()
                        self.store.commit()
                        self.qmlogger.warning('Source %s is deleted' % source_name)
                    else:
                        self.qmlogger.info('Not deleted anything.')
                        
        for index in range(len(self.sources)):
            # Check output type
            if (not (4>self.sources[index].outputtype>0)):
                self.qmlogger.error('output_type must be between 1-3, please look at the definition.\n')

            # Check list type
            list_id = self.store.find(List.id, List.type == unicode(self.sources[index].listtype)).one()
            if list_id is None:
                self.qmlogger.warning('List type couldn\'t be found in the database, please check your configuration.')
                self.qmlogger.warning('Assigning default list type value.')
                list_id = 1 #means default unknown list type

            # Calculate the checksum
            conf_checksum = hashlib.md5()   
            conf_checksum.update(self.sources[index].sourcename + str(self.sources[index].listtype) + 
                                 self.sources[index].sourcelink + self.sources[index].sourcefile    +
                                 self.sources[index].parser     + str(self.sources[index].time_interval) )
            source_checksum = self.store.find(Source.checksum, Source.name == unicode(self.sources[index].sourcename)).one()
            if source_checksum is None:
                # Adding new source
                self.qmlogger.info('Adding new source %s' % self.sources[index].sourcename)
                # Add new parser
                parser = Parser()
                parser.name = unicode(self.sources[index].parser)
                parser.time_interval = self.sources[index].time_interval 
                self.store.add(parser)
                self.store.flush()
                # Add new source
                source = Source()
                source.name = unicode(self.sources[index].sourcename)
                source.link = unicode(self.sources[index].sourcelink)
                source.list_id = list_id
                source.parser_id = parser.id
                source.checksum = unicode(conf_checksum.hexdigest())
                self.store.add(source)
                # Commit changes
                self.store.commit()
                self.qmlogger.info('New Source added successfully : "%s"' % self.sources[index].sourcename)
            elif str(conf_checksum.hexdigest()) == str(source_checksum):
                self.qmlogger.info('No need to reconfigure the source : %s' % self.sources[index].sourcename)
            elif str(conf_checksum.hexdigest()) != str(source_checksum):
                # Update source information
                self.qmlogger.info('Updating the source %s' % self.sources[index].sourcename)
                # Update existing source
                source = self.store.find(Source, Source.name == '%s' % unicode(self.sources[index].sourcename) ).one()
                source.link = unicode(self.sources[index].sourcelink)
                source.list_id = list_id
                source.checksum = unicode(conf_checksum.hexdigest())
                self.store.add(source)
                # Update existing parser
                parser = self.store.find(Parser, Parser.id == source.parser_id).one()
                parser.name = unicode(self.sources[index].parser)
                parser.time_interval = self.sources[index].time_interval
                self.store.add(parser)
                # Commit changes
                self.store.commit()
                self.qmlogger.info('Source updated successfully : "%s"' % self.sources[index].sourcename)
            else:
                self.qmlogger.error('CHECK CODE')
                self.qmlogger.warning('conf checksum ' + conf_checksum.hexdigest())
                self.qmlogger.warning('source_checksum ' + source_checksum)
                sys.exit()
        # reconfigure subscription types 
        self.createSubscriptionTypes()
        sys.exit()


   # Parser Management 
    def checkParsers(self):
        '''
            Check if the parser exists in the given path.
        '''
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        for index in range(len(self.sources)):
            if os.path.exists(self.sources[index].parser):
                self.qmlogger.info('Parser "%s" Exists, OK!' % self.sources[index].parser)
            else:
                self.qmlogger.warning('Parser %s doesn\'t exist\nPlease check the nfquery.conf file' % self.sources[index].parser)

    
    def executeParsers(self, parser=None):
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        if parser is None:
            self.qmlogger.debug('running all parsers')
            for index in range(len(self.sources)):
                try:
                    returncode = subprocess.call(['python', self.sources[index].parser])
                    if returncode == 0:
                        self.queryGenerator.createQuery(self.sources[index].parser)
                    else:
                        self.qmlogger.warning('Parser returned with error')
                except Exception, e:
                    self.qmlogger.error('got exception: %r, exiting' % (e))
                    continue
        else:
            self.qmlogger.debug('running parser %s' % parser)
            for index in range(len(self.sources)):
                if self.sources[index].parser == parser:
                    try:
                        returncode = subprocess.call(['python', self.sources[index].parser])
                        if returncode == 0:
                            self.queryGenerator.createQuery(self.sources[index].parser)
                        else:
                            self.qmlogger.warning('Parser returned with error')
                    except Exception, e:
                        self.qmlogger.error('got exception: %r, exiting' % (e))
                        continue


    #  == Subscription Management ==
    
    # Subscription Types Creation 
    def createSubscriptionTypes(self):
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        '''
            We have 2 different subscription types.
            
            1) Source -> example : "Amada,Malc0de,DFN-Honeypot,ABC-NREN_Special_Source"
            2) List Type -> example : "Botnet,Malware,Honeypot Output, Special Source Output"
            
            These subscription types are inserted into subscription table
            according to the condition of "if that subscription type have queries" 
            in query table. "createSubscriptions" function fills the subscription 
            table by inserting these subscription types. 
    
    		!!!!!! SUBSCRIPTION_TAGS NE OLACAK !!!!!!!!
    
        '''
    
        # 1) Source Name
        subscription_type=1
        source_name_list = self.store.find(Source.name)
        source_name_list.group_by(Source.name)
        for source_name in source_name_list:
            subscription = self.store.find(Subscription.id, Subscription.name == '%s' % (source_name))
            if subscription.is_empty():
                subscription = Subscription()
                subscription.type = subscription_type
                subscription.name = source_name
                self.store.add(subscription)
                self.qmlogger.debug('Subscription type %s added to db' % source_name)
    
        # 2) List Type
        subscription_type=2
        list_type_list = self.store.find(List.type)
        list_type_list.group_by(List.type)
        for list_type in list_type_list:
            subscription = self.store.find(Subscription.id, Subscription.name == '%s' % (list_type))
            if subscription.is_empty():
                subscription = Subscription()
                subscription.type = subscription_type
                subscription.name = list_type
                self.store.add(subscription)
                self.qmlogger.debug('Subscription type %s added to db' % list_type)

        self.store.commit()
        self.qmlogger.debug('Subscription types are created')
    
    
    # Subscription Packets Creation 
    def createSubscriptionPackets(self):
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.qmlogger.info('Generating Subscriptions...')
        self.createSourceSubscriptionPackets()
        self.createListSubscriptionPackets()
    
    
    def createSourceSubscriptionPackets(self):
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        # If source_name is not given, we work for all sources.
        source_name_list = self.store.find(Subscription.name, Subscription.type == 1)
        if source_name_list is None:
            self.qmlogger.error("Source is not registered to database. Run 'reconfig sources' or check sources.")
            #sys.exit()
            return None
        for source_name in source_name_list:
            source_id = self.store.find(Source.id, Source.name == '%s' % unicode(source_name)).one()
            query_id_list = self.store.find(Query.id, Query.source_id == source_id)
            if query_id_list is None:
                self.qmlogger.warning("We don't have any query for this source.")
                self.qmlogger.warning("%s subscription creation is failed." % (source_name) )
                continue
            subscription_id = self.store.find(Subscription.id, Subscription.name == '%s' % unicode(source_name)).one()
            subs_packet_id = self.store.find(SubscriptionPackets.id, SubscriptionPackets.subscription_id == subscription_id).one()
            if subs_packet_id is None:
                for qid in query_id_list:
                    spacket = SubscriptionPackets()
                    spacket.subscription_id = subscription_id
                    spacket.query_id = qid
                    self.store.add(spacket)
                self.qmlogger.debug('Source subscription packets are created')
            else:
                query_ids = self.store.find(SubscriptionPackets.query_id, SubscriptionPackets.subscription_id == subscription_id)
                for qid in query_id_list:
                    if not (qid in query_ids):
                        spacket = SubscriptionPackets(subscription_id, qid)
                        self.store.add(spacket)
                self.qmlogger.debug('Source subscription packets are created2')
        self.store.commit()
    
    
    def createListSubscriptionPackets(self):
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        list_type_list = self.store.find(Subscription.name, Subscription.type == 2)
        if list_type_list is None:
            self.qmlogger.error("List type is not registered to subscriptions. Run reconfig or check sources.")
            #sys.exit()
            return None
        for list_type in list_type_list:
            list_id = self.store.find(List.id, List.type == '%s' % unicode(list_type)).one()
            source_id = self.store.find(Source.id, Source.list_id == list_id)
            if source_id.is_empty():
                continue
            query_id_list = self.store.find(Query.id, In(Query.source_id, list(source_id)))
            if not query_id_list.is_empty():
                subscription_id = self.store.find(Subscription.id, Subscription.name == '%s' % unicode(list_type)).one()
                subs_packet_id = self.store.find(SubscriptionPackets.id, SubscriptionPackets.subscription_id == subscription_id)
                if subs_packet_id.is_empty():
                    for qid in query_id_list:
                        spacket = SubscriptionPackets()
                        spacket.subscription_id = subscription_id
                        spacket.query_id = qid
                        self.store.add(spacket)
                    self.qmlogger.debug('List subscription packets are created')
                else:
                    query_ids = self.store.find(SubscriptionPackets.query_id, SubscriptionPackets.subscription_id == subscription_id)
                    for qid in query_id_list:
                        if not (qid in query_ids):
                            spacket = SubscriptionPackets()
                            spacket.subscription_id = subscription_id
                            spacket.query_id = qid
                            self.store.add(spacket)
                    self.qmlogger.debug('List subscription packets are added2')
            else:
                self.qmlogger.warning("We don't have any query for this list type.")
                self.qmlogger.warning("%s subscription is not created." % (list_type))
        self.store.commit()
    
    # Subscription Releasing and Handling Plugin Requests
    def getSubscription(self, name):
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        subscription_id = self.store.find(Subscription.id, Subscription.name == unicode(name)).one()
        self.qmlogger.debug('subscription_id = %d' % subscription_id)
        if not (subscription_id is None):
            self.qmlogger.debug('y1')
            squery_id_list = self.store.find(SubscriptionPackets.query_id, SubscriptionPackets.subscription_id == subscription_id)
            if not squery_id_list.is_empty():
                self.qmlogger.debug('y2')
                query_id_list = self.store.find(Query.id, In(Query.id, list(squery_id_list)))
                if not query_id_list.is_empty():
                    self.qmlogger.debug('y3')
                    ip_id_list = self.store.find(QueryIP.ip_id, In(QueryIP.query_id, list(query_id_list)))
                    if not ip_id_list.is_empty():
                        self.qmlogger.debug('y4')
                        ip_list = self.store.find(IP.ip, In(IP.id, list(ip_id_list)))
                        for i in ip_list:
                            self.qmlogger.debug(i)
                        if not ip_list.is_empty():
                            self.qmlogger.debug('y5')
                            return list(ip_list)
                            self.qmlogger.debug('Returning subscription information : %s' % name)
        self.qmlogger.warning('Couldn\'t get subscription information : %s ' % name)
        return None


    def getAllSubscriptions(self):
        self.qmlogger.debug('In %s' % sys._getframe().f_code.co_name)
        subscription_list = self.store.find(Subscription.name)
        print list(subscription_list)
        return list(subscription_list)


            