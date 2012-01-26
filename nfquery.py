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
from logger  import ColoredLogger
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
if __name__ == "__main__":
    # Parse Command Line Arguments
    parser = argparse.ArgumentParser(description="Process arguments")
    parser.add_argument('--conf', type=str, required=True, help='nfquery configuration file')
    parser.add_argument('--debug', action='store_true', help='enable debug mode')
    parser.add_argument('--reconfig', action='store_true', help='reconfigure sources')
    args = parser.parse_args()

    # Start Logging Module
    logging.setLoggerClass(ColoredLogger)
    nfquerylog = logging.getLogger('nfquery')

    if args.debug:
        # Enable Debugging
		nfquerylog.setLevel(logging.DEBUG)
		defaults.loglevel = logging.DEBUG
    else:
		# Log info messages
		nfquerylog.setLevel(logging.INFO)
		defaults.loglevel = logging.INFO
   
    multiprocessing.log_to_stderr()
    #sys.stdout = nfquerylog

    # Parse Config File
    try:
        config_file = Config(args.conf)
    except Exception, e:
        nfquerylog.info("Please check configuration file syntax")
        nfquerylog.info("Here is the error details:")
        nfquerylog.info("%s" % e)
        sys.exit()
   
    nfquerylog.info('Starting NfQuery...')
    nfquerylog.debug('Parsing configuration file options')

    # Prepare Config File Sections
    ConfigSections = { 
                       'nfquery'  : ['path','sources_path','host','port','ipv6', 'logfile'], 
                       'database' : ['db_host','db_name','db_user','db_password'], 
                       'sources'  : ['sourcename','sourcelink','sourcefile','listtype','outputtype','outputfile','parser','time_interval']
                     }

    # Check Config File Sections
    sections = config_file.keys()
    if(set(ConfigSections.keys()).issubset(set(sections))):
        nfquerylog.info('Main configuration options are OK')
        for section,option in config_file.iteritems():
            # Check if the section has a loop like 'sources' option.
            if hasattr(option, 'keys') and hasattr(option, '__getitem__'):
                nfquerylog.debug('This section is a mapping')
                if (set(ConfigSections[section]).issubset(set(option.keys()))):
                    nfquerylog.debug(str(ConfigSections[section]) + 'exists')
                else:
                    nfquerylog.info(str(ConfigSections[section]) + ' option does not exists in the configuration file.')
                    nfquerylog.info('Please add the required option to conf file and check the manual')
                    sys.exit()
            elif hasattr(option, '__iter__'):
                nfquerylog.debug('This section is a sequence')
                if (set(ConfigSections[section]).issubset(set(option[0].keys()))):
                    nfquerylog.debug(str(ConfigSections[section]) + 'exists')
                else:
                    nfquerylog.info(str(ConfigSections[section]) + ' option does not exists in the configuration file.')
                    nfquerylog.info('Please add the required option to conf file and check the manual')
                    sys.exit()
            else:
                nfquerylog.info('Unknown configuration file option value, Check the code!')
                sys.exit()
    else:
        nfquerylog.info('One of the main configuration options does not exists')
        nfquerylog.info('You should have all \'nfquery, database, sources\' options in the conf file')
        nfquerylog.info('Please add the required option and check the manual')
    
	# Check if we reconfigure sources
    if args.reconfig:
        nfquerylog.info("Reconfiguring sources")
        defaults.reconfigure_flag = args.reconfig
    else:
        nfquerylog.info("'Not reconfiguring, daily routine ;)")

    # 1) Check if paths are correct 
    # 2) Test for database connection   
    # Start Database Connection
    database = db(config_file.database.db_host, config_file.database.db_user, config_file.database.db_password, config_file.database.db_name)
    connection = database.get_database_connection()

    # Start Query Generator 
    q_generator = QueryGenerator(config_file.sources)
    q_generator.run()
    #q_generator.createQuery()

    # Start the scheduler
    nfquerylog.info('Starting the scheduler')
    sched = Scheduler()
    sched.start()

    for index in range(len(config_file.sources)):
        ## Schedule job_function to be called every two hours
        nfquerylog.debug('Adding job to scheduler : %s', config_file.sources[index].parser)
        sched.add_interval_job(q_generator.executeParsers, args=[config_file.sources[index].parser], minutes=config_file.sources[index].time_interval, start_date='2012-01-18 09:30') 
        #sched.add_interval_job(q_generator.executeParsers, args=[config_file.sources[index].parser], minutes=1, start_date='2012-01-18 09:30')
        #sched.add_interval_job(q_generator.executeParsers, hours=3) 

    # Server Start
    server = SocketServer.ThreadingTCPServer((config_file.nfquery.host, config_file.nfquery.port), ThreadingTCPRequestHandler)

    # This will keep running the server until interrupting it with the keyboard Ctrl-C or something else.
    try:
        nfquerylog.info('listening for plugin connections...')
        server.serve_forever()
    except KeyboardInterrupt:
        nfquerylog.debug('keyboard Interrupt')
        # Database Connection End
        database.close_database_connection()

