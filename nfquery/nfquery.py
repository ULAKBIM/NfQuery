#!/usr/local/bin/python

import os
import time
import logging
import argparse
import resource
import threading
import multiprocessing
import atexit
import SocketServer
import MySQLdb


from apscheduler.scheduler import Scheduler
from datetime import date
from config import Config, ConfigError

# package imports
from db import *
from db2 import db2
from querygenerator import *
from subscription import *
from logger  import createLogger
from defaults import defaults


######################################################
# Special Imports For Twisted JSON_RPC  -> txjsonrpc
from twisted.web import server
from twisted.internet import ssl,reactor
#from twisted.internet.protocol import Factory
#from twisted.application import service,internet

#from txjsonrpc.web import jsonrpc
from twjsonrpc import Example
######################################################


class NfQueryServer:
    
    def __init__(self, configfile, loglevel=None):
        # start logging
        defaults.loglevel = loglevel
        self.nfquerylog = createLogger('nfquery', loglevel)
        
        # Parse Config File
        try:
            self.config = Config(configfile)
        except ConfigError, e:
            self.nfquerylog.info("Please check configuration file syntax")
            self.nfquerylog.info("%s" % e)
            sys.exit(1)
   
        self.nfquerylog.debug('Parsing configuration file options')

        # Prepare Config File Sections
        ConfigSections = {
            'nfquery'  : ['path','sources_path','host','port','ipv6', 'cert_file', 'key_file', 'logfile'], 
            'plugins'  : ['organization', 'adm_name', 'adm_mail', 'adm_tel', 'adm_publickey_file', 'prefix_list', 'plugin_ip'],
            'database' : ['db_host','db_name','db_user','db_password'], 
            'sources'  : ['sourcename','sourcelink','sourcefile','listtype','outputtype','outputfile','parser','time_interval']
        }

        # Check Config File Sections
        sections = self.config.keys()
        if(set(ConfigSections.keys()).issubset(set(sections))):
            self.nfquerylog.debug('Main configuration options are OK')
            for section,option in self.config.iteritems():
                # Check if the section has a loop like 'sources' option.
                if hasattr(option, 'keys') and hasattr(option, '__getitem__'):
                    self.nfquerylog.debug('This section is a mapping')
                    if (set(ConfigSections[section]).issubset(set(option.keys()))):
                        self.nfquerylog.debug(str(ConfigSections[section]) + 'exists')
                    else:
                        #self.nfquerylog.error(str(ConfigSections[section]) + ' option does not exists in the configuration file.')
                        #self.nfquerylog.error('Please add the required option to conf file and check the manual')
                        raise ConfigError(str(ConfigSections[section]) + ' option does not exists in the configuration file.' + 
                                          'Please add the required option to conf file and check the manual' )
                elif hasattr(option, '__iter__'):
                    self.nfquerylog.debug('This section is a sequence')
                    if (set(ConfigSections[section]).issubset(set(option[0].keys()))):
                        self.nfquerylog.debug(str(ConfigSections[section]) + 'exists')
                    else:
                        self.nfquerylog.info(str(ConfigSections[section]) + ' option does not exists in the configuration file.')
                        self.nfquerylog.info('Please add the required option to conf file and check the manual')
                        sys.exit(1)
                else:
                    self.nfquerylog.info('Unknown configuration file option value, Check the code!')
                    sys.exit(1)
        else:
            self.nfquerylog.info('One of the main configuration options does not exists')
            self.nfquerylog.info('You should have all \'nfquery, database, sources\' options in the conf file')
            self.nfquerylog.info('Please add the required option and check the manual')


    def startScheduler(self):
        '''
            Schedule parsers to be called according to time interval parameter of in conf file.
            Schedule other related jobs.
        '''
        self.sched = Scheduler()
        for index in range(len(self.config.sources)):
            self.nfquerylog.debug('Adding job to scheduler : %s, time interval is = %d', self.config.sources[index].parser, 
                                   self.config.sources[index].time_interval)
            self.sched.add_interval_job(self.q_generator.executeParsers, args=[self.config.sources[index].parser], 
                                   minutes=self.config.sources[index].time_interval, start_date='2012-01-18 09:30')
            #self.sched.add_interval_job(self.q_generator.executeParsers, args=[self.config.sources[index].parser], 
            #                       minutes=2, start_date='2012-01-18 09:30') 
        self.sched.start()
        self.nfquerylog.info('Started the scheduler')
    
 
    def startJSONRPCServer(self):
        '''
            Start Json RPC Server, bind to socket and listen for incoming connections from plugins.
        '''
        try:
            r = Example()
            exserver = server.Site(r)
            #return internet.SSLServer(7777, exserver, ssl.DefaultOpenSSLContextFactory('certs/nfquery.key', 'certs/nfquery.crt'))
            
            # without method parameter
            #reactor.listenSSL(7777, exserver, ssl.DefaultOpenSSLContextFactory(self.config.nfquery.key_file, self.config.nfquery.cert_file))
            # default one
            #reactor.listenSSL(7777, exserver, ssl.DefaultOpenSSLContextFactory(self.config.nfquery.key_file, self.config.nfquery.cert_file, sslmethod=ssl.SSL.SSLv23_METHOD))
            # test for tlsv1
            reactor.listenSSL(self.config.nfquery.port, exserver, ssl.DefaultOpenSSLContextFactory(self.config.nfquery.key_file, self.config.nfquery.cert_file, sslmethod=ssl.SSL.TLSv1_METHOD))
            self.nfquerylog.info('listening for plugin connections...')
        except KeyboardInterrupt:
            self.nfquerylog.debug('keyboard Interrupt')
            self.stop()


    def start(self):
        '''
            Starting all modules.
        ''' 
        
        # Start Database Connection
        #self.database = db( self.config.database.db_host, self.config.database.db_user, 
        #                    self.config.database.db_password, self.config.database.db_name )
        #self.connection = self.database.get_database_connection()
       
        from db2 import db2
        self.db = db2( self.config.database.db_host, self.config.database.db_user,
                       self.config.database.db_password, self.config.database.db_name )
        self.store = self.db.get_store()
 
        # Start Query Generator 
        self.q_generator = QueryGenerator(self.config.sources, self.store)
        self.q_generator.run()
        
        # Start network server
        #self.startJSONRPCServer()
        
        # Start scheduler
        #self.startScheduler()

        self.nfquerylog.info('QueryServer started on port %s' % self.config.nfquery.port)
       
        # Shutdown handler
        atexit.register(self.stop)

                
    def stop(self, signum=None, frame=None):
        # close database
        #self.server.shutdown()
        self.database.close_database_connection()
        self.nfquerylog.info('QueryServer is stopped')
        # Stop reactor
        if reactor.running:
            reactor.stop()


    def reconfigure(self, flag):
        # Start Database Connection
        #self.database = db( self.config.database.db_host, self.config.database.db_user, 
        #                    self.config.database.db_password, self.config.database.db_name )
        #self.connection = self.database.get_database_connection()

        self.db = db2( self.config.database.db_host, self.config.database.db_user,
                       self.config.database.db_password, self.config.database.db_name )
        self.store = self.db.get_store()

        if flag == 'sources':
            self.q_generator = QueryGenerator(self.store, sources=self.config.sources)
            self.q_generator.reconfigureSources()
        elif flag == 'plugins':
            self.q_generator = QueryGenerator(self.store, plugins=self.config.plugins)
            self.q_generator.reconfigurePlugins()
        else:
            self.nfquerylog.error('Unknown option for reconfigure function, quitting.')
            sys.exit(1)
 

    def run(self):
        reactor.callWhenRunning(self.start)
        reactor.run()

