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



# nfquery imports
from db import *
from querygenerator import *
from subscription import *
#from ColoredFormatter import ColoredLogger
#from ansistrm import ColorizingStreamHandler

# ------------------------------------------------------------------------------------- #
class nfquery(multiprocessing.Process):
    def run():
        pass

class get:
    #path = "/usr/local/nfquery"
    path = "/home/serdar/nfquery"
    sources_path = path + "/parsers"

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

class ThreadingTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    daemon_threads=True
    allow_reuse_address=True
    def __init__(self, server_address, RequestHandlerClass):
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)

# ------------------------------------------------------------------------------------- #
if __name__ == "__main__":
    #multiprocessing.log_to_stderr(logging.INFO)

    logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    logging.setLoggerClass(ColoredFormatter)
    
    ################ Quick and Dirty Solution for Color Formatting ######################################## 
    # logging.addLevelName(logging.DEBUG, "\033[1;31m%s\033[1;m" % logging.getLevelName(logging.DEBUG))
    # logging.addLevelName(logging.INFO, "\033[1;36m%s\033[1;m" % logging.getLevelName(logging.INFO))
    # logging.addLevelName(logging.WARNING, "\033[1;31m%s\033[1;m" % logging.getLevelName(logging.WARNING))
    # ################ Quick and Dirty Solution for Color Formatting ######################################## 
    
    #logging.basicConfig(level=logging.DEBUG)
    nfquerylog = logging.getLogger('nfquery')
    nfquerylog.add
    #nfquerylog.addHandler(ColorizingStreamHandler())
    nfquerylog.debug('Starting NfQuery...')
    nfquerylog.debug('Parsing command line arguments')

    # Parse Command Line Arguments
    parser = argparse.ArgumentParser(description="Process arguments")
    parser.add_argument('config_file', metavar="--conf", type=str, nargs='?', help='nfquery configuration file')
    args = parser.parse_args()

    # Parse Config File
    #configkeys = {'nfquery':'','database','sources'}
    try:
        config_file = Config(args.config_file)
    except Exception, e:
        nfquerylog.info("Please check configuration file syntax\n")
        nfquerylog.info("Here is the error details:\n")
        nfquerylog.info("%s" % e)
        sys.exit()

    # Prepare Config File Sections
    ConfigSections = { 
                       'nfquery'  : ['path','sources_path','host','port','ipv6'], 
                       'database' : ['db_host','db_name','db_user','db_password'], 
                       'sources'  : ['sourcename','listtype','sourcelink','sourcefile','parser']
                     }

    # Check Config File Sections
    sections = config_file.keys()
    if(set(sections).issubset(set(ConfigSections.keys()))):
        nfquerylog.info('Main configuration options are OK')
        for section,option in config_file.iteritems():
            # Check if the section has a loop like 'sources' option.
            if hasattr(option, 'keys') and hasattr(option, '__getitem__'):
                nfquerylog.debug('This section is a mapping')
                if (set(ConfigSections[section]).issubset(set(option.keys()))):
                    nfquerylog.debug(str(ConfigSections[section]) + 'exists')
                else:
                    nfquerylog.info(str(ConfigSections[section]) + ' option does not exists in the configuration file.')
                    nfquerylog.info('Please add the required option and check configuration file manual')
                    sys.exit()
            elif hasattr(option, '__iter__'):
                nfquerylog.debug('This section is a sequence')
                if (set(ConfigSections[section]).issubset(set(option[0].keys()))):
                    nfquerylog.debug(str(ConfigSections[section]) + 'exists')
                else:
                    nfquerylog.info(str(ConfigSections[section]) + ' option does not exists in the configuration file.')
                    nfquerylog.info('Please add the required option and check configuration file manual')
                    sys.exit()
            else:
                nfquerylog.info('Unknown configuration file option value, Check the code!')
                sys.exit()
    else:
        nfquerylog.info('One of the main configuration options does not exists')
        nfquerylog.info('Please add the required option and check configuration file manual')



        #print type(items[1])

    #print dir(config_file)
    sys.exit()

    # Test DB Connection
    dbdbd
    # Start Database Connection
    database = db(config_file.database.db_host, config_file.database.db_user, config_file.database.db_password, config_file.database.db_name)
    connection = database.get_database_connection()

    get.path = config_file.nfquery.path
    get.sources_path = config_file.nfquery.sources_path

    # Check if source information configured correctly
    if not config_file.sources:
        nfquerylog.warning('Please configure source information in nfquery.conf file\n')
        sys.exit()

    # Start Query Generator
    q_generator = QueryGenerator(config_file.sources)
    q_generator.start()


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

