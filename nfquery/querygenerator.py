#!/usr/local/bin/python

import simplejson as json
import logging
import multiprocessing
import sys
import os.path
import hashlib
import MySQLdb
import subprocess
import time

# nfquery imports
import db
import subscription
from query import query
from defaults import defaults
from logger import createLogger
from utils import query_yes_no
from models import *


__all__ = ['QueryGenerator']

class QueryGenerator:
    #def __init__(self, store, sources=None, plugins=None):
    def __init__(self, sources=None, plugins=None):
        self.qglogger = createLogger('QueryGenerator', defaults.loglevel)
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.store = db.get_store()
        self.sources = sources
        self.plugins = plugins
         

    def run(self):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.checkParsers()
        self.executeParsers()
        subscription.createSubscriptions()


    def checkParsers(self):
        '''
            Check if the parser exists in the given path.
        '''
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        for index in range(len(self.sources)):
            if os.path.exists(self.sources[index].parser):
                self.qglogger.info('Parser "%s" Exists, OK!' % self.sources[index].parser)
            else:
                self.qglogger.warning('Parser %s doesn\'t exist\nPlease check the nfquery.conf file' % self.sources[index].parser)

    
    def executeParsers(self, parser=None):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        if parser is None:
            self.qglogger.debug('running all parsers')
            for index in range(len(self.sources)):
                try:
                    returncode = subprocess.call(['python', self.sources[index].parser])
                    if returncode == 0:
                        self.createQuery(self.sources[index].parser)
                    else:
                        self.qglogger.warning('Parser returned with error')
                except Exception, e:
                    self.qglogger.error('got exception: %r, exiting' % (e))
                    continue
        else:
            self.qglogger.debug('running parser %s' % parser)
            for index in range(len(self.sources)):
                if self.sources[index].parser == parser:
                    try:
                        returncode = subprocess.call(['python', self.sources[index].parser])
                        if returncode == 0:
                            self.createQuery(self.sources[index].parser)
                        else:
                            self.qglogger.warning('Parser returned with error')
                    except Exception, e:
                        self.qglogger.error('got exception: %r, exiting' % (e))
                        continue


    def reconfigurePlugins(self):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.qglogger.info('Reconfiguring plugins')

        dbplugins = self.store.find(Plugin)
        
        # Maintain the table for delete operations
        if dbplugins.count() > 0:
            plugins_list = []
            for index in range(len(self.plugins)):
                plugins_list.append(self.plugins[index].organization)
            for plugin in dbplugins:
                if not plugin.organization in(plugins_list):
                    self.qglogger.warning('I will delete the plugin, Do you approve the deletion of plugin : %s',plugin.organization)
                    flag = query_yes_no('', default="no")
                    if flag is True:
                        plugin_name = plugin.organization
                        prefix_id = plugin.prefix_id
                        self.store.find(Plugin, Plugin.organization == plugin.organization).remove()
                        self.store.find(PrefixList, PrefixList.prefix_id == prefix_id).remove()
                        self.store.commit()
                        self.qglogger.warning('Plugin %s is deleted' % plugin_name)
                    else:
                        self.qglogger.info('Not deleted anything.')
        
        for index in range(len(self.plugins)):
            # Calculate the checksum
            conf_checksum = hashlib.md5()
            conf_checksum.update( self.plugins[index].organization       + self.plugins[index].adm_name    + 
                                  self.plugins[index].adm_mail           + self.plugins[index].adm_tel     +          
                                  self.plugins[index].adm_publickey_file + self.plugins[index].prefix_list +
                                  self.plugins[index].plugin_ip )
            plugin_checksum = self.store.find(Plugin.checksum, Plugin.organization == unicode(self.plugins[index].organization)).one()

            if plugin_checksum is None:
                self.qglogger.info('Adding new plugin : "%s"' % self.plugins[index].organization)
                plugin = Plugin()
                prefix_list = PrefixList()
                prefix_list.prefix   = unicode(self.plugins[index].prefix_list)
                self.store.add(prefix_list)
                self.store.flush()
                plugin.organization = unicode(self.plugins[index].organization)
                plugin.adm_name = unicode(self.plugins[index].adm_name)
                plugin.adm_mail = unicode(self.plugins[index].adm_mail)
                plugin.adm_tel = unicode(self.plugins[index].adm_tel)
                plugin.adm_publickey_file = unicode(self.plugins[index].adm_publickey_file)
                plugin.plugin_ip = unicode(self.plugins[index].plugin_ip)
                plugin.prefix_id = prefix_list.prefix_id
                plugin.checksum = unicode(conf_checksum.hexdigest())
                self.store.add(plugin)
                self.store.commit()
                self.qglogger.debug(plugin.plugin_id)
                self.qglogger.debug(prefix_list.prefix_id)
                self.qglogger.info('New Plugin added successfully : "%s"' % self.plugins[index].organization)
            elif plugin_checksum == conf_checksum.hexdigest():
                self.qglogger.info('No need to update the plugin : %s' % self.plugins[index].organization)
            elif plugin_checksum != conf_checksum.hexdigest():
                # Update plugin information
                self.qglogger.info('Updating the plugin %s' % self.plugins[index].organization)
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
                prefix_list = self.store.find(PrefixList, PrefixList.prefix_id == plugin.prefix_id).one()
                prefix_list.prefix  = unicode(self.plugins[index].prefix_list)
                self.store.add(prefix_list)
                # Commit changes
                self.store.commit()
                self.qglogger.info('Plugin updated successfully : "%s"' % self.plugins[index].organization)
            else:
                self.qglogger.error('CHECK CODE')
                self.qglogger.warning('conf checksum ' + conf_checksum.hexdigest())
                self.qglogger.warning('plugin_checksum ' + plugin_checksum)
        sys.exit()


    def reconfigureSources(self):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.qglogger.info('Reconfiguring sources')

        dbsources = self.store.find(Source)
        
        # Maintain the table for delete operations
        if dbsources.count() > 0:
            sources_list = []
            for index in range(len(self.sources)):
                sources_list.append(self.sources[index].sourcename)
            for source in dbsources:
                if not source.source_name in(sources_list):
                    self.qglogger.warning('I will delete the source, Do you approve the deletion of source : %s', source.source_name)
                    flag = query_yes_no('', default="no")
                    if flag is True:
                        source_name = source.source_name
                        list_id = source.list_id
                        parser_id = source.parser_id
                        self.store.find(Source, Source.source_name == source.source_name).remove()
                        self.store.find(Parser, Parser.parser_id == parser_id).remove()
                        self.store.commit()
                        self.qglogger.warning('Source %s is deleted' % source_name)
                    else:
                        self.qglogger.info('Not deleted anything.')
                        
        for index in range(len(self.sources)):
            # Check output type
            if (not (4>self.sources[index].outputtype>0)):
                self.qglogger.error('output_type must be between 1-3, please look at the definition.\n')

            # Check list type
            list_id = self.store.find(List.list_id, List.list_type == unicode(self.sources[index].listtype)).one()
            if list_id is None:
                self.qglogger.warning('List type couldn\'t be found in the database, please check your configuration.')
                self.qglogger.warning('Assigning default list type value.')
                list_id = 1 #means default unknown list type

            # Calculate the checksum
            conf_checksum = hashlib.md5()   
            conf_checksum.update(self.sources[index].sourcename + str(self.sources[index].listtype) + 
                                 self.sources[index].sourcelink + self.sources[index].sourcefile    +
                                 self.sources[index].parser     + str(self.sources[index].time_interval) )
            source_checksum = self.store.find(Source.checksum, Source.source_name == unicode(self.sources[index].sourcename)).one()
            if source_checksum is None:
                # Adding new source
                self.qglogger.info('Adding new source %s' % self.sources[index].sourcename)
                # Add new parser
                parser = Parser()
                parser.parser_script = unicode(self.sources[index].parser)
                parser.time_interval = self.sources[index].time_interval 
                self.store.add(parser)
                self.store.flush()
                # Add new source
                source = Source()
                source.source_name = unicode(self.sources[index].sourcename)
                source.source_link = unicode(self.sources[index].sourcelink)
                source.list_id = list_id
                source.parser_id = parser.parser_id 
                source.checksum = unicode(conf_checksum.hexdigest())
                self.store.add(source)
                # Commit changes
                self.store.commit()
                self.qglogger.info('New Source added successfully : "%s"' % self.sources[index].sourcename)
            elif str(conf_checksum.hexdigest()) == str(source_checksum):
                self.qglogger.info('No need to reconfigure the source : %s' % self.sources[index].sourcename)
            elif str(conf_checksum.hexdigest()) != str(source_checksum):
                # Update source information
                self.qglogger.info('Updating the source %s' % self.sources[index].sourcename)
                # Update existing source
                source = self.store.find(Source, Source.source_name == '%s' % unicode(self.sources[index].sourcename) ).one()
                source.source_link = unicode(self.sources[index].sourcelink)
                source.list_id = list_id
                source.checksum = unicode(conf_checksum.hexdigest())
                self.store.add(source)
                # Update existing parser
                parser = self.store.find(Parser,Parser.parser_id == source.parser_id).one()
                parser.parser_script = unicode(self.sources[index].parser)
                parser.time_interval = self.sources[index].time_interval
                self.store.add(parser)
                # Commit changes
                self.store.commit()
                self.qglogger.info('Source updated successfully : "%s"' % self.sources[index].sourcename)
            else:
                self.qglogger.error('CHECK CODE')
                self.qglogger.warning('conf checksum ' + conf_checksum.hexdigest())
                self.qglogger.warning('source_checksum ' + source_checksum)
                sys.exit()
        # reconfigure subscription types 
        subscription.createSubscriptionTypes()
        sys.exit()

 
    def createQuery(self, parsername=None):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        if parsername is None:
            for index in range(len(self.sources)):
                try:
                    outputfile = open(self.sources[index].outputfile, 'r')
                    data = json.load(outputfile)
                    #self.qglogger.debug('%s, %s, %s ' % (data['source_name'], data['update_time'], data['ip_list']))
                    outputfile.close()
                except Exception, e:
                    self.qglogger.warning('got exception: %r' % (e))
                    self.qglogger.warning('could not load output of parser %s' % self.sources[index].parser)
                    continue
                # Check values with db and conf file.
                # source_name, listtype, output and update time check should be done here!!!!
                myquery = query(data['source_name'], data['output_type'], data['ip_list'], data['update_time'])
                myquery.insert_query(self.store)
        else:
            for index in range(len(self.sources)):
                if parsername == self.sources[index].parser:
                    try:
                        outputfile = open(self.sources[index].outputfile, 'r')
                        data = json.load(outputfile)
                        outputfile.close()
                    except Exception, e:
                        self.qglogger.warning('got exception: %r' % (e))
                        self.qglogger.warning('could not create queries for parser %s' % parsername)
                        continue
                    # Check values with db and conf file.
                    # source_name, outputtype, output and update time check should be done here!!!!
                    myquery = query(data['source_name'], data['output_type'], data['ip_list'], data['update_time'])
                    myquery.insert_query(self.store)
        self.qglogger.debug('end of createQuery')

            
