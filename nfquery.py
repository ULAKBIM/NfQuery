#!/usr/local/bin/python

import os
import time
import logging
import argparse
import resource
import threading
import MySQLdb
import multiprocessing
import SocketServer

from apscheduler.scheduler import Scheduler
from datetime import date
from config import Config, ConfigError

# package imports
from db import *
from querygenerator import *
from subscription import *
from jsonrpcserver import ThreadingTCPRequestHandler
from logger  import createLogger
from defaults import defaults

SLEEP_TIME = 5


class rpc_func:
    def add(x,y):
        return x+y 
    def register(prefix_list, mailaddress ):
        pass
        # Assume we handled the https issue and pki
        # So client verified itself, we trust him now.

        


class nfquery:
    
    def __init__(self, pid_file=None):
        # start logging
        self.nfquerylog = createLogger('nfquery')
        
        if pid_file == None:
            self.pid_file = '/tmp/nfquery.pid'
        else:
            self.pid_file = pid_file

        # Parse and Test configuration
        try:
            self.parseAndTest()
        except Exception, e:
            self.nfquerylog.error('%s', e)
            sys.exit(1)
        

    def parseAndTest(self):
        # 1) Check if paths are correct 
        # 2) Test for database connection   
        self.parser = argparse.ArgumentParser(description="Process command line arguments")
        self.parser.add_argument('--conf', type=str, required=True, help='nfquery configuration file')
        self.parser.add_argument('--debug', action='store_true', help='enable debug mode')
        self.parser.add_argument('--reconfig', action='store_true', help='reconfigure sources')
        self.parser.add_argument('--daemon', action='store_true', help='reconfigure sources')
        

		# Parse command line arguments	
        args = self.parser.parse_args()

        if args.debug:
            # Enable Debugging
            self.nfquerylog.setLevel(logging.DEBUG)
            defaults.loglevel = logging.DEBUG
        else:
            # Enable Info Logging
            self.nfquerylog.setLevel(logging.INFO)
            defaults.loglevel = logging.INFO
   
        #sys.stdout = self.nfquerylog
        if not os.path.isfile(args.conf):
            raise ValueError('Configuration file not found: {}'.format(
                args.conf))

        # Parse Config File
        try:
            self.config_file = Config(args.conf)
        except ConfigError, e:
            self.nfquerylog.info("Please check configuration file syntax")
            self.nfquerylog.info("%s" % e)
            sys.exit(1)
   
        self.nfquerylog.debug('Parsing configuration file options')

        # Prepare Config File Sections
        ConfigSections = {
                           'nfquery'  : ['path','sources_path','host','port','ipv6', 'cert_file', 'key_file', 'logfile'], 
                           'database' : ['db_host','db_name','db_user','db_password'], 
                           'sources'  : ['sourcename','sourcelink','sourcefile','listtype','outputtype','outputfile','parser','time_interval']
                         }

        # Check Config File Sections
        sections = self.config_file.keys()
        if(set(ConfigSections.keys()).issubset(set(sections))):
            self.nfquerylog.debug('Main configuration options are OK')
            for section,option in self.config_file.iteritems():
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
        
        # Check if we reconfigure sources
        if args.reconfig:
            self.nfquerylog.info("Reconfiguring sources")
            defaults.reconfigure_flag = args.reconfig
        else:
            self.nfquerylog.info("'Not reconfiguring, daily routine ;)")


        # Check if we run it as daemon
        if args.daemon:
            self.daemon_flag = True
            self.nfquerylog.info("Running as daemon")
        else:
            self.daemon_flag = False
            self.nfquerylog.info("Running as no daemon")
    

    def startScheduler(self):
        '''
            Schedule parsers to be called according to time interval parameter of in conf file.
            Schedule other related jobs.
        '''
        self.sched = Scheduler()
        self.sched.start()
        for index in range(len(self.config_file.sources)):
            self.nfquerylog.debug('Adding job to scheduler : %s', self.config_file.sources[index].parser)
            self.sched.add_interval_job(self.q_generator.executeParsers, args=[self.config_file.sources[index].parser], 
                                   minutes=self.config_file.sources[index].time_interval, start_date='2012-01-18 09:30') 

    
    def setupServer1(self):
        from jsonrpcserver import ThreadingTCPRequestHandler
        self.server = SocketServer.ThreadingTCPServer((self.config_file.nfquery.host, self.config_file.nfquery.port) , ThreadingTCPRequestHandler)
        #self.server.register_function(lambda x,y: x+y, 'add')

    def setupServer2(self):
        from parsers.jsonRPCTest.SimpleJSONRPCServer import SimpleJSONRPCServer
        self.server = SimpleJSONRPCServer(("localhost", 8000))
        #self.server.register_function(lambda x,y: x+y, 'add')
        self.server.register_function(rpc_func)

    def setupServer3(self):
        from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
        self.server = SimpleJSONRPCServer((self.config_file.nfquery.host, self.config_file.nfquery.port))
        self.server.register_function(rpc_func)

    def setupServer4(self):
        from SecureJSONRPCServer import SecureJSONRPCServer
        self.server = SecureJSONRPCServer((self.config_file.nfquery.host, self.config_file.nfquery.port), 
                                           certFile=self.config_file.nfquery.cert_file, keyFile=self.config_file.nfquery.key_file )
        self.server.register_function(rpc_func)

    def startJSONRPCServer(self):
        '''
            Start Json RPC Server, bind to socket and listen for incoming connections from plugins.
        '''

        # TEST Servers
        #self.setupServer1()
        #self.setupServer2()
        self.setupServer3()
        #self.setupServer4()
        
        # This will keep running the server until interrupting it with the keyboard Ctrl-C or something else.
        try:
            jsonRPCServer = threading.Thread(target=self.server.serve_forever)
            jsonRPCServer.daemon = True
            jsonRPCServer.start()
            self.nfquerylog.info('listening for plugin connections...')
        except KeyboardInterrupt:
            self.nfquerylog.debug('keyboard Interrupt')
            self.stop()


    def _daemonize(self):
        """
            Create daemon process.
        
            Based upon recipe provided at
            http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/278731
        """
        
        self.nfquerylog.debug('Daemonizing...')
        
        UMASK = 0
        # ????
        WORKDIR = '/'
        MAXFD = 1024 
        
        if hasattr(os, 'devnull'):
            REDIRECT_TO = os.devnull
        else:
            REDIRECT_TO = '/dev/null'

        # double fork
        try :
            if os.fork() != 0:
                os._exit(0)

            print 'a'
            os.setsid()

            print 'b'
            if os.fork() != 0:
                os._exit(0)

            print 'c'
            os.chdir(WORKDIR)
            os.umask(UMASK)
        
            print 'd'
        except OSError, e:
            self.nfquerylog('exception: %s %s', e.strerror, e.errno)
            raise Exception, "%s [%d]" % (e.strerror, e.errno)
        except Exception, e:
            self.nfquerylog('exception: %s', str(e))

        # Use the getrlimit method to retrieve the maximum file descriptor number
        # that can be opened by this process.  If there is not limit on the
        # resource, use the default value.
        #
        # from  http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/278731
        #
        maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        if maxfd == resource.RLIM_INFINITY:
            maxfd = MAXFD
        for fd in range(0, maxfd):
            # syslog uses fd 3, we shouldn't close it on systems where the
            # service is running. The child process will inherit it.
            if fd == 3: continue
            try:
                os.close(fd)
            except OSError:
                pass

        # This call to open is guaranteed to return the lowest file descriptor,
        # which will be 0 (stdin), since it was closed above.
        os.open(REDIRECT_TO, os.O_RDWR)         # standard output (0)

        # Duplicate standard input to standard output and standard error.
        os.dup2(0, 1)                           # standard output (1)
        os.dup2(0, 2)                           # standard output (2)


    def start(self):
        '''
            Starting all modules.
        ''' 
        import signal
        # To handle os signals
        signal.signal(signal.SIGTERM, self.stop)

        if self.daemon_flag:
            self._daemonize()

        # permission denied ???
        if self.pid_file:
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))

        # Start Database Connection
        self.database = db( self.config_file.database.db_host, self.config_file.database.db_user, 
                            self.config_file.database.db_password, self.config_file.database.db_name )
        self.connection = self.database.get_database_connection()
        # Start Query Generator 
        self.q_generator = QueryGenerator(self.config_file.sources)
        self.q_generator.run()
        # Start network server
        self.startJSONRPCServer()
        # Start scheduler
        self.nfquerylog.info('Starting the scheduler')
        self.startScheduler()

        logging.info('QueryServer started on port %s' % self.config_file.nfquery.port)

        # get in to infinite loop
        self.request_stop = False
        while not self.request_stop:
            time.sleep(SLEEP_TIME)

                
    def stop(self, signum=None, frame=None):
        # close database
        self.server.shutdown()
        self.database.close_database_connection()
        self.request_stop = True
        self.nfquerylog.info('QueryServer is stopped')
        sys.exit(0)



# ------------------------------------------------------------------------------------- #


def go():
    try:
        QueryServer = nfquery()
    except Exception, e:
        logging.critical('PROBLEM! %s', e)
        sys.exit(1)

    try:
        QueryServer.start()
    except KeyboardInterrupt:
        QueryServer.stop()
    

if __name__ == "__main__":
	# Just because we can't call __main__ from /usr/bin/nfquery,
	# and setuptools need this to run the program correctly.
	go()


