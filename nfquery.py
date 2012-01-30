#!/usr/local/bin/python

from datetime import date
from config import Config
import multiprocessing
import os
import SocketServer
import argparse
import MySQLdb
import time
import logging

from apscheduler.scheduler import Scheduler

# nfquery imports
from db import *
from querygenerator import *
from subscription import *
from logger  import createLogger
from defaults import defaults

# ------------------------------------------------------------------------------------- #
# class nfquery(multiprocessing.Process):
#    def run():
#        pass
# ------------------------------------------------------------------------------------- #

class ThreadingTCPRequestHandler(SocketServer.BaseRequestHandler):
    '''
        The RequestHandler class for our server.

        It is instantiated once per connection to the server, and must
        override the handle() method to implement communication to the
        client.
    '''
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "%s wrote:" % self.client_address[0]
        print self.data
        # just send back the same data, but upper-cased
        self.request.send(self.data.upper())

#class ThreadingTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
#    daemon_threads=True
#    allow_reuse_address=True
#    def __init__(self, server_address, RequestHandlerClass):
#        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)
#        print 'used'
#        # start logging
#        logging.setLoggerClass(ColoredLogger)
#        self.slogger = logging.getLogger('ThreadingTCPServer')
#        self.slogger.setLevel(defaults.loglevel)
#        self.slogger.info('Server is initiated')

# ------------------------------------------------------------------------------------- #

class nfquery:
    
    def __init__(self):
        self.nfquerylog = createLogger('nfquery')


    def parseAndTest(self):
        self.parser = argparse.ArgumentParser(description="Process arguments")
        self.parser.add_argument('--conf', type=str, required=True, help='nfquery configuration file')
        self.parser.add_argument('--debug', action='store_true', help='enable debug mode')
        self.parser.add_argument('--reconfig', action='store_true', help='reconfigure sources')
        args = self.parser.parse_args()

        if args.debug:
            # Enable Debugging
            self.nfquerylog.setLevel(logging.DEBUG)
            defaults.loglevel = logging.DEBUG
        else:
            # Log info messages
            self.nfquerylog.setLevel(logging.INFO)
            defaults.loglevel = logging.INFO
   
        #sys.stdout = self.nfquerylog

        # Parse Config File
        try:
            self.config_file = Config(args.conf)
        except Exception, e:
            self.nfquerylog.info("Please check configuration file syntax")
            self.nfquerylog.info("Here is the error details:")
            self.nfquerylog.info("%s" % e)
            sys.exit()
   
        self.nfquerylog.info('Starting NfQuery...')
        self.nfquerylog.debug('Parsing configuration file options')

        # Prepare Config File Sections
        ConfigSections = {
                           'nfquery'  : ['path','sources_path','host','port','ipv6', 'logfile'], 
                           'database' : ['db_host','db_name','db_user','db_password'], 
                           'sources'  : ['sourcename','sourcelink','sourcefile','listtype','outputtype','outputfile','parser','time_interval']
                         }

        # Check Config File Sections
        sections = self.config_file.keys()
        if(set(ConfigSections.keys()).issubset(set(sections))):
            self.nfquerylog.info('Main configuration options are OK')
            for section,option in self.config_file.iteritems():
                # Check if the section has a loop like 'sources' option.
                if hasattr(option, 'keys') and hasattr(option, '__getitem__'):
                    self.nfquerylog.debug('This section is a mapping')
                    if (set(ConfigSections[section]).issubset(set(option.keys()))):
                        self.nfquerylog.debug(str(ConfigSections[section]) + 'exists')
                    else:
                        self.nfquerylog.info(str(ConfigSections[section]) + ' option does not exists in the configuration file.')
                        self.nfquerylog.info('Please add the required option to conf file and check the manual')
                        sys.exit()
                elif hasattr(option, '__iter__'):
                    self.nfquerylog.debug('This section is a sequence')
                    if (set(ConfigSections[section]).issubset(set(option[0].keys()))):
                        self.nfquerylog.debug(str(ConfigSections[section]) + 'exists')
                    else:
                        self.nfquerylog.info(str(ConfigSections[section]) + ' option does not exists in the configuration file.')
                        self.nfquerylog.info('Please add the required option to conf file and check the manual')
                        sys.exit()
                else:
                    self.nfquerylog.info('Unknown configuration file option value, Check the code!')
                    sys.exit()
        else:
            self.nfquerylog.info('One of the main configuration options does not exists')
            self.nfquerylog.info('You should have all \'nfquery, database, sources\' options in the conf file')
            self.nfquerylog.info('Please add the required option and check the manual')
        
        # Check if we reconfigure sources
        if args.reconfig:
            self.nfquerylog.info("Reconfiguring sources")
            defaults.reconfigure_flag = args.reconfig
        else:
            self.nfquerylog.info("'Not reconfiguring, daily routine ;)")


    def startScheduler(self):
        '''
            Schedule parsers to be called according to time interval parameter of in conf file.
            Schedule other related jobs.
        '''
        sched = Scheduler()
        sched.start()
        for index in range(len(self.config_file.sources)):
            self.nfquerylog.debug('Adding job to scheduler : %s', self.config_file.sources[index].parser)
            sched.add_interval_job(self.q_generator.executeParsers, args=[self.config_file.sources[index].parser], minutes=self.config_file.sources[index].time_interval, 
                                   start_date='2012-01-18 09:30') 


    def startNetworkServer(self):
        '''
            Start Json RPC Server, bind to socket and listen for incoming connections from plugins.
        '''
        self.server = SocketServer.ThreadingTCPServer((self.config_file.nfquery.host, self.config_file.nfquery.port), ThreadingTCPRequestHandler)
        # This will keep running the server until interrupting it with the keyboard Ctrl-C or something else.
        try:
            self.nfquerylog.info('listening for plugin connections...')
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.nfquerylog.debug('keyboard Interrupt')
            self.stop()


    def start(self):


        # 1) Check if paths are correct 
        # 2) Test for database connection   

        self.parseAndTest() 

        # Start Database Connection
        self.database = db(self.config_file.database.db_host, self.config_file.database.db_user, self.config_file.database.db_password, self.config_file.database.db_name)
        self.connection = self.database.get_database_connection()

        # Start Query Generator 
        self.q_generator = QueryGenerator(self.config_file.sources)
        self.q_generator.run()

        # Start the scheduler
        self.nfquerylog.info('Starting the scheduler')
        self.startScheduler()

        # Start the server
        self.startNetworkServer()

                
    def stop(self):    
        # close database
        self.server.shutdown()
        self.database.close_database_connection()





# ------------------------------------------------------------------------------------- #




if __name__ == "__main__":
    # Parse Command Line Arguments

    QueryServer = nfquery()
    QueryServer.start()
    
