# -*- coding: utf-8 -*-
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

import os
import sys
import time
import logging
import resource
#SIL# import threading
import multiprocessing
import atexit
from datetime import date
from config import Config, ConfigError

from storm.locals import *
from storm.exceptions import (Error)

from MySQLdb import Error as MySQLException

# package imports

import logger
from querymanager import QueryManager

######################################################
# Special Imports For Twisted JSON_RPC  -> txjsonrpc

from twisted.web import server
from twisted.internet import ssl,reactor
from OpenSSL import SSL
from twisted.internet import task
#from twisted.internet.protocol import Factory
#from twisted.application import service,internet

from jsonrpc import jsonRPCServer
######################################################

class QueryServer:

    def __init__(self, configfile, loglevel=None):

        # start logging
        logger.LOGLEVEL = loglevel
        self.qslogger = logger.createLogger('queryserver')

#SIL#        self.dbTablesAreOk = False
        self.database = None

        # Parse Config File
        try:
            self.config = Config(configfile)
        except ConfigError, e:
            self.qslogger.info('Please check configuration file syntax')
            self.qslogger.info('%s' % e)
            sys.exit(1)

        self.qslogger.debug('Parsing configuration file options')

        # Prepare Config File Sections

        ConfigSections = {
            'nfquery': [ 'path', 'sources_path', 'host', 'port', 'ipv6', 'cert_file', 'key_file', 'logfile', ],
            'plugins': [ 'organization', 'adm_name', 'adm_mail', 'adm_tel', 'adm_publickey_file', 'prefix_list', 'plugin_ip', ],
            'database': ['db_host', 'db_name', 'db_user', 'db_password' ],
            'sources': [ 'source_name', 'source_link', 'source_file', 'threat_type', 'output_file', 'parser', 'time_interval', ],
            }

        # Check Config File Sections
        # self.qslogger.debug(self.config)

        sections = self.config.keys()
        if set(ConfigSections.keys()).issubset(set(sections)):
            self.qslogger.debug('Main configuration options are OK')
            for (section, option) in self.config.iteritems():

                # print section,option
                # print dir(option)
                # Check if the section has a loop like 'sources' option.

                if hasattr(option, 'keys') and hasattr(option, '__getitem__') and option:
                    if set(ConfigSections[section]).issubset(set(option.keys())):
                        self.qslogger.debug(str(ConfigSections[section]) + 'exists')
                    else:
                        raise ConfigError(str(ConfigSections[section]) + ' option does not exists in the configuration file.' + 'Please add the required option to conf file and check the manual')
                elif hasattr(option, '__iter__') and (option):
                    if (set(ConfigSections[section]).issubset(set(option[0].keys()))):
                        self.qslogger.debug(str(ConfigSections[section]) + 'exists')
                    else:
                        self.qslogger.info(str(ConfigSections[section]) + ' option does not exists in the configuration file.')
                        self.qslogger.info('Please add the required option to conf file and check the manual')
                        sys.exit(1)
                else:
                    self.qslogger.info('Unknown configuration file option, Check the code!')
                    sys.exit(1)
        else:
            self.qslogger.info('One of the main configuration options does not exists')
            self.qslogger.info('You should have all \'nfquery, database, plugin, sources\' options in the configuration file')
            self.qslogger.info('Please add the required option and check the manual')

    def verifyCallback(self, connection, x509, errnum, errdepth, ok):
        if not ok:
            self.qslogger.error('Invalid Cert from Subject: %s' % (x509.get_subject()))
            return False
        return True

    def startJSONRPCServer(self):
        '''
            Start Json RPC Server, bind to socket and listen for incoming connections from plugins.
        '''

        rpcserver = server.Site(jsonRPCServer(self))

        # sslmethod = ssl.SSL.SSLv23_METHOD and other could be implemented here.
        # For TLSV1

        contextFactory = ssl.DefaultOpenSSLContextFactory(self.config.nfquery.key_file,
                self.config.nfquery.cert_file,
                sslmethod=ssl.SSL.SSLv23_METHOD)
        ctx = contextFactory.getContext()
        ctx.set_verify(SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT, self.verifyCallback)

        # Since we have self-signed certs we have to explicitly
        # tell the server to trust them.

        ctx.load_verify_locations(self.config.nfquery.root_cert_file)
        reactor.listenSSL(self.config.nfquery.port, rpcserver, contextFactory)

        self.qslogger.info('Starting QueryServer')
        self.qslogger.info('Listening for plugin connections on port : %s' % self.config.nfquery.port)

    def executeParsers(self, parser):
        qm = QueryManager(store=self.createStore(), sources=self.config.sources, plugins=self.config.plugins)
        qm.executeParsers(parser)
        # cleanup
        qm.store.close()
        qm = None

    def startScheduler(self):
        '''
            Schedule parsers to be called according to time interval parameter indicated in conf file.
        '''

        for index in range(len(self.config.sources)):
            # routine = task.LoopingCall(self.queryManager.executeParsers, self.config.sources[index].parser)  # call the parser
            routine = task.LoopingCall(self.executeParsers, self.config.sources[index].parser)  # call the parser
            routine.start(int(self.config.sources[index].time_interval) * 60, now=False)  # call according to time interval in seconds
        self.qslogger.info('Starting the Scheduler')

    def start(self):
        '''
            Starting all modules.
        '''

        # Start Database Connection

        self.store = self.createStore()
        self.initializeDBIfNeeded()

        # Check if configuration file has changed or not
        # If changed run reconfig sources or reconfig plugins.
        # ASSUME THAT WE HANDLED HERE!!
        # So db and conf file is consistent.

        # Start QueryManager

        queryManager = QueryManager(store = self.store, sources=self.config.sources, plugins=self.config.plugins)
        queryManager.start()
        self.store.close();
        queryManager = None

        # Start JSONRPCServer
        self.startJSONRPCServer()

        # Start Scheduler
        self.startScheduler()

        # Set shutdown handler
        atexit.register(self.stop)

    def stop(self):
        # Stop reactor and exit

        if reactor.running:
            reactor.stop()
        self.qslogger.info('QueryServer is stopped')
        sys.exit()

    def reconfigure(self, flag):
        # Start Database Connection

        self.store = self.createStore()

        # Start Query Manager

        if flag == 'sources':
            self.queryManager = QueryManager(store=self.store, sources=self.config.sources)
            self.queryManager.reconfigureSources()
        elif flag == 'plugins':
            self.queryManager = QueryManager(store=self.store, plugins=self.config.plugins)
            self.queryManager.reconfigurePlugins()



    def run(self):
        self.start()
        reactor.run()


################################ DB ######################################
# functions defined in db.py are imported here as QueryServer methods

    def initialize_db(self):
        self.store.execute('CREATE TABLE time ('
                      + 'id int(10) unsigned NOT NULL AUTO_INCREMENT,'
                      + 'time datetime NOT NULL,' + 'PRIMARY KEY (id)'
                      + ') ENGINE=InnoDB AUTO_INCREMENT=13357 DEFAULT CHARSET=utf8;'
                      )
        self.store.execute('CREATE TABLE category ('
                      + 'id int(10) unsigned NOT NULL AUTO_INCREMENT,'
                      + 'category varchar(20) NOT NULL,'
                      + 'PRIMARY KEY (id)'
                      + ') ENGINE=InnoDB  DEFAULT CHARSET=utf8')
        self.store.execute('CREATE TABLE type ('
                      + 'id int(10) unsigned NOT NULL AUTO_INCREMENT,'
                      + 'type varchar(40) NOT NULL,' + 'PRIMARY KEY (id)'
                      + ') ENGINE=InnoDB DEFAULT CHARSET=utf8')
        self.store.execute('CREATE TABLE prefix('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'prefix TEXT  COLLATE utf8_unicode_ci NOT NULL,'
                      + 'PRIMARY KEY (id)'
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE application ('
                      + 'id int(10) unsigned NOT NULL AUTO_INCREMENT,'
                      + 'version int(10) unsigned NOT NULL,'
                      + 'creation_time varchar(20) NOT NULL,'
                      + 'PRIMARY KEY (id)'
                      + ') ENGINE=InnoDB DEFAULT CHARSET=utf8')
    
        self.store.execute('CREATE TABLE plugin ('
                      + 'id int(10) unsigned NOT NULL AUTO_INCREMENT,'
                      + 'organization varchar(30) COLLATE utf8_unicode_ci NOT NULL,'
    
                      + 'adm_name varchar(30) COLLATE utf8_unicode_ci NOT NULL,'
    
                      + 'adm_mail varchar(30) COLLATE utf8_unicode_ci NOT NULL,'
    
                      + 'adm_tel varchar(20) COLLATE utf8_unicode_ci NOT NULL,'
    
                      + 'adm_publickey_file varchar(50) COLLATE utf8_unicode_ci NOT NULL,'
                       + 'prefix_id int(10) unsigned NOT NULL,'
                      + 'plugin_ip varchar(20) COLLATE utf8_unicode_ci NOT NULL,'
    
                      + 'checksum varchar(32) COLLATE utf8_unicode_ci NOT NULL,'
                       + 'registered INT NOT NULL,' + 'PRIMARY KEY (id),'
                      + 'UNIQUE KEY plugin_ip (plugin_ip),'
                      + 'KEY prefix_id (prefix_id),'
                      + 'CONSTRAINT plugin_ibfk_1 FOREIGN KEY (prefix_id) REFERENCES prefix (id)'
    
                      + ') ENGINE=InnoDB AUTO_INCREMENT=70 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;'
                      )
    
        self.store.execute('CREATE TABLE parser('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'name VARCHAR(75) COLLATE utf8_unicode_ci NOT NULL,'
                       + 'time_interval SMALLINT(6) NOT NULL,'
                      + 'checksum varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL, '
                       + 'PRIMARY KEY (id)'
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE threat('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'type VARCHAR(20) COLLATE utf8_unicode_ci NOT NULL,'
                       + 'UNIQUE KEY type (type),' + 'PRIMARY KEY (id)'
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE source('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'name VARCHAR(75) COLLATE utf8_unicode_ci NOT NULL,'
                       + 'parser_id INT UNSIGNED NOT NULL,'
                      + 'checksum VARCHAR(32) COLLATE utf8_unicode_ci NOT NULL,'
    
                      + 'link VARCHAR(75) COLLATE utf8_unicode_ci NOT NULL,'
                       + 'is_active INT UNSIGNED NOT NULL,'
                      + 'threat_id int unsigned NOT NULL,'
                      + 'FOREIGN KEY (threat_id) REFERENCES threat (id),'
                      + 'FOREIGN KEY (parser_id) REFERENCES parser (id) ON UPDATE CASCADE,'
                       + 'PRIMARY KEY (id)'
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE query ('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'source_id INT UNSIGNED NOT NULL,'
                      + 'update_time_id int(10) unsigned DEFAULT NULL,'
                      + 'type SMALLINT UNSIGNED NOT NULL,'
                      + 'checksum VARCHAR(32) NOT NULL,'
                      + 'creation_time_id int(10) unsigned NOT NULL,'
                      + 'type_id int(10) unsigned NOT NULL,'
                      + 'category_id int(10) unsigned NOT NULL,'
                      + 'PRIMARY KEY (id),'
                      + 'FOREIGN KEY (source_id) REFERENCES source(id) ON DELETE CASCADE'
    
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE alert ('
                      + 'id int(10) unsigned NOT NULL AUTO_INCREMENT,'
                      + 'alert_type int(10) unsigned NOT NULL,'
                      + 'query_id int(10) unsigned NOT NULL,'
                      + 'identified_plugin_id int(10) unsigned NOT NULL,'
                      + 'identifier_plugin_id int(10) unsigned,'
                      + 'start_time int(11) unsigned NOT NULL,'
                      + 'end_time int(11) unsigned NOT NULL,'
                      + 'first_seen int(11) unsigned NOT NULL,'
                      + 'checksum varchar(32) COLLATE utf8_unicode_ci NOT NULL,'
                       + 'PRIMARY KEY (id),'
                      + 'FOREIGN KEY (identified_plugin_id) REFERENCES plugin(id) ON DELETE CASCADE,'
    
                      + 'FOREIGN KEY (identifier_plugin_id) REFERENCES plugin(id) ON DELETE CASCADE,'
                       + 'FOREIGN KEY (query_id) REFERENCES query(id)'
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )  # "FOREIGN KEY (start_time_id) REFERENCES time(id) ON DELETE CASCADE,"                    +
                         # "FOREIGN KEY (end_time_id) REFERENCES time(id) ON DELETE CASCADE,"                      +
    
        self.store.execute('CREATE TABLE query_packet ('
                      + 'id int(10) unsigned NOT NULL AUTO_INCREMENT,'
                      + 'validation_id int(10) unsigned NOT NULL,'
                      + 'query_id int(10) unsigned NOT NULL,'
                      + 'PRIMARY KEY (id),'
                      + 'KEY validation_id (validation_id),'
                      + 'KEY query_id (query_id),'
                      + 'CONSTRAINT query_packet_ibfk_1 FOREIGN KEY (validation_id) REFERENCES query (id) ON DELETE CASCADE,'
    
                      + 'CONSTRAINT query_packet_ibfk_2 FOREIGN KEY (query_id) REFERENCES query (id) ON DELETE CASCADE'
    
                      + ')ENGINE=InnoDB AUTO_INCREMENT=15086 DEFAULT CHARSET=utf8'
                      )
    
        self.store.execute('CREATE TABLE subscription('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'type SMALLINT unsigned NOT NULL,'
                      + 'name VARCHAR(50) COLLATE utf8_unicode_ci NOT NULL,'
                       + 'PRIMARY KEY (id),' + 'UNIQUE KEY name (name)'
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE subscription_packet ('
                      + 'id int(10) unsigned NOT NULL AUTO_INCREMENT,'
                      + 'subscription_id int(10) unsigned NOT NULL,'
                      + 'query_packet_id int(10) unsigned NOT NULL,'
                      + 'PRIMARY KEY (id),'
                      + 'KEY subscription_id (subscription_id),'
                      + 'KEY query_packet_id (query_packet_id),'
                      + 'CONSTRAINT subscription_packet_ibfk_1 FOREIGN KEY (subscription_id) REFERENCES subscription (id),'
    
                      + 'CONSTRAINT subscription_packet_ibfk_2 FOREIGN KEY (query_packet_id) REFERENCES query_packet (id) ON DELETE CASCADE'
    
                      + ') ENGINE=InnoDB AUTO_INCREMENT=35836 DEFAULT CHARSET=utf8;'
                      )
    
        self.store.execute('CREATE TABLE ip('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'ip VARCHAR(20) COLLATE utf8_unicode_ci NOT NULL,'
                      + 'ip_int BIGINT(20) UNSIGNED NOT NULL,'
                      + 'PRIMARY KEY (id)'
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE src_ip('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'query_id INT UNSIGNED NOT NULL,'
                      + 'ip_id INT UNSIGNED NOT NULL,'
                      + 'FOREIGN KEY (ip_id) REFERENCES ip(id) ON DELETE CASCADE,'
    
                      + 'FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE,'
                       + 'PRIMARY KEY (id)'
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE dst_ip('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'query_id INT UNSIGNED NOT NULL,'
                      + 'ip_id INT UNSIGNED NOT NULL,'
                      + 'FOREIGN KEY (ip_id) REFERENCES ip(id) ON DELETE CASCADE,'
    
                      + 'FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE,'
                       + 'PRIMARY KEY (id)'
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE port('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'port INT UNSIGNED NOT NULL,' + 'PRIMARY KEY (id)'
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE src_port('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'query_id INT UNSIGNED NOT NULL,'
                      + 'port_id INT UNSIGNED NOT NULL,'
                      + 'FOREIGN KEY (port_id) REFERENCES port(id) ON DELETE CASCADE,'
    
                      + 'FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE,'
                       + 'PRIMARY KEY (id)'
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE dst_port('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'query_id INT UNSIGNED NOT NULL,'
                      + 'port_id INT UNSIGNED NOT NULL,'
                      + 'FOREIGN KEY (port_id) REFERENCES port(id) ON DELETE CASCADE,'
    
                      + 'FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE,'
                       + 'PRIMARY KEY (id)'
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE proto('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'query_id INT UNSIGNED NOT NULL,'
                      + 'proto VARCHAR(3) NOT NULL,' + 'PRIMARY KEY (id),'
                      + 'FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE'
    
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE protocol_version('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'query_id INT UNSIGNED NOT NULL,'
                      + 'protocol_version VARCHAR(4) NOT NULL,'
                      + 'PRIMARY KEY (id),'
                      + 'FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE'
    
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE packets('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'query_id INT UNSIGNED NOT NULL,'
                      + 'packets INT UNSIGNED NOT NULL,'
                      + 'PRIMARY KEY (id),'
                      + 'FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE'
    
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE bytes('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'query_id INT UNSIGNED NOT NULL,'
                      + 'bytes INT UNSIGNED NOT NULL,' + 'PRIMARY KEY (id),'
    
                      + 'FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE'
    
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE bps('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'query_id INT UNSIGNED NOT NULL,'
                      + 'bps INT UNSIGNED NOT NULL,' + 'PRIMARY KEY (id),'
                      + 'FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE'
    
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE pps('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'query_id INT UNSIGNED NOT NULL,'
                      + 'bps INT UNSIGNED NOT NULL,' + 'PRIMARY KEY (id),'
                      + 'FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE'
    
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE bpp('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'query_id INT UNSIGNED NOT NULL,'
                      + 'bpp INT UNSIGNED NOT NULL,' + 'PRIMARY KEY (id),'
                      + 'FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE'
    
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE duration('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'query_id INT UNSIGNED NOT NULL,'
                      + 'duration INT UNSIGNED NOT NULL,'
                      + 'PRIMARY KEY (id),'
                      + 'FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE'
    
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE tos('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'query_id INT UNSIGNED NOT NULL,'
                      + 'tos TINYINT UNSIGNED NOT NULL,'
                      + 'PRIMARY KEY (id),'
                      + 'FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE'
    
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE flags('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'query_id INT UNSIGNED NOT NULL,'
                      + 'flags VARCHAR(20) NOT NULL,' + 'PRIMARY KEY (id),'
                      + 'FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE'
    
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE scale('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'query_id INT UNSIGNED NOT NULL,'
                      + 'scale VARCHAR(1) NOT NULL,' + 'PRIMARY KEY (id),'
                      + 'FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE'
    
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE asn('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'query_id INT UNSIGNED NOT NULL,'
                      + 'asn VARCHAR(20) NOT NULL,' + 'PRIMARY KEY (id),'
                      + 'FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE'
    
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
        self.store.execute('CREATE TABLE statistics('
                      + 'id INT UNSIGNED NOT NULL AUTO_INCREMENT,'
                      + 'alert_id INT UNSIGNED NOT NULL,'
                      + 'number_of_flows INT UNSIGNED NOT NULL,'
                      + 'number_of_bytes INT UNSIGNED NOT NULL,'
                      + 'number_of_packets INT UNSIGNED NOT NULL,'
                      + 'PRIMARY KEY (id),'
                      + 'FOREIGN KEY (alert_id) REFERENCES alert(id) ON DELETE CASCADE'
    
                      + ')ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci'
                      )
    
    
    def insert_threats(self):
        # import logger
    
        from models import Threat
    
        # threat_list = ['Generic', 'Other', 'Botnet', 'Malware', 'Spam', 'Phishing', 'DNSBL', 'Worm', 'Honeypot' ]
    
        threat_list = ['Botnet', 'Spam']
    
        for name in threat_list:
            threat = Threat()
            threat.type = unicode(name)
            self.store.add(threat)
            self.store.flush()
        self.store.commit()
    
        # logger.info('Threat list is inserted into database.')
    
        self.qslogger.info('Threat list is inserted into database.')
    
    
    def insert_type(self):
        # import logger
    
        from models import Type
        type_list = [
            '0',
            '1',
            '0,2,1,3',
            '0,3',
            '0,2,3',
            '0,2,3',
            '0,1,3',
            ]
    
        for name in type_list:
            type = Type()
            type.type = unicode(name)
            self.store.add(type)
            self.store.flush()
        self.store.commit()
    
        # logger.info('Type list is inserted into database.')
    
        self.qslogger.info('Type list is inserted into database.')
    
    
    def insert_category(self):
        # import logger
    
        from models import Category
        category_list = ['validation', 'mandatory', 'optional']
        for name in category_list:
            category = Category()
            category.category = unicode(name)
            self.store.add(category)
            self.store.flush()
        self.store.commit()
    
        # logger.info('Category list is inserted into database.')
    
        self.qslogger.info('Category list is inserted into database.')
    
    def setStore(self, store):
        self.store = store
        self.queryManager.setStore(store)
    
    def createStore(self):
        '''
            Create and return a database connection if not exists yet.
        '''
        
        if (self.database is None):
            db = 'mysql://' + self.config.database.db_user + ':' + self.config.database.db_password + '@' + self.config.database.db_host + '/' + self.config.database.db_name
            self.database = create_database(db)

        return Store(self.database)



    def initializeDBIfNeeded(self):
        try:
            result = self.store.execute('SELECT version FROM application')
            if result:
                return True

        except MySQLException, e:
            if e.args[0] == 1146:
                self.qslogger.info('Creating the tables')
                self.initialize_db()
                self.insert_threats()
                self.insert_type()
                self.insert_category()
                self.store.flush()
                return True
            else:
                self.qslogger.error('Unhandled DB Error' + e + '. Exiting...')
                sys.exit(1)
        except Exception, e:
            self.qslogger.error(e)
            self.qslogger.error('Exiting...')
            sys.exit(1)


    def dbEnsureConnected(self, store = None):
        try:
            if (store is None):
                    self.store.execute("SELECT 1")
                    return (self.store)
            else:
                    store.execute("SELECT 1")
                    return (store)
        except Error, exc:
            self.qslogger.info(exc)
            self.qslogger.info("Database reconnection will be done.")
            if (store is None):
                self.setStore(self.createStore())
                return (self.store)
            else:
                return (self.createStore())
#            if self.store.is_disconnection_error(exc):
#            else:
#                raise

