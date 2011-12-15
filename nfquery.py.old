#!/usr/local/bin/python

from datetime import date
from config import Config
import ConfigParser
# it is changed as configparser, supdate the python and change it as
# import configparser
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
#from ansistrm import ColorizingStreamHandler

# ------------------------------------------------------------------------------------- #
                        ####################### 
                        #       NFQUERY       #
                        ####################### 
class nfquery(multiprocessing.Process):
    def run():
        pass


# ------------------------------------------------------------------------------------- #
                        ####################### 
                        #       NETWORKING    #
                        ####################### 

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
                        ####################### 
                        #       MAIN          #
                        ####################### 

if __name__ == "__main__":
    #multiprocessing.log_to_stderr(logging.DEBUG)

    # LOGGING ' e bir coloring mekanizmasi lazim!!!!!!!
    logging.basicConfig(level=logging.DEBUG)
    nfquerylog = logging.getLogger('nfquery')
    #nfquerylog.addHandler(ColorizingStreamHandler())
    nfquerylog.debug('Starting NfQuery...')
    nfquerylog.debug('Parsing command line arguments')

    # Parse Command Line Arguments
    parser = argparse.ArgumentParser(description="Process arguments")
    parser.add_argument('config_file', metavar="--conf", type=str, nargs='?', help='nfquery configuration file')
    args = parser.parse_args()

    config_file = Config(args.config_file)

    # Parse Configuration File
    # CONFIGPARSER # parser = ConfigParser.ConfigParser()
    # CONFIGPARSER # parser.read(args.config_file)

    # CONFIGPARSER # sections = ['GENERAL', 'DATABASE']
    # CONFIGPARSER # generaloptions = ['path','parsers_path','parsers_output_path','host', 'port', 'ipv6']

    # CONFIGPARSER # # Parsing default options
    # CONFIGPARSER # for section in sections:
    # CONFIGPARSER #     if parser.has_section(section): 
    # CONFIGPARSER #         nfquerylog.debug('Parsing Section:%s' % section)
    # CONFIGPARSER #         nfquerylog.debug('Options:')
    # CONFIGPARSER #         for name, value in parser.items(section):
    # CONFIGPARSER #             nfquerylog.debug('\t%s = %s' % (name, value))
    # CONFIGPARSER #     else:
    # CONFIGPARSER #         nfquerylog.debug('Section `%s` does not exists' % section )
    # CONFIGPARSER #         nfquerylog.debug('Please add it and edit the nfquery.conf file as indicated in the documentation')
    # CONFIGPARSER #         sys.exit()

    # CONFIGPARSER # # Parsing parser options 
    # CONFIGPARSER # section_prefix = 'PARSER'
    # CONFIGPARSER # index=1
    # CONFIGPARSER # section = section_prefix + str(index)
    # CONFIGPARSER # while parser.has_section(section):
    # CONFIGPARSER #     nfquerylog.debug('Parsing Section:%s' % section)
    # CONFIGPARSER #     nfquerylog.debug('Options:')
    # CONFIGPARSER #     keys = ['parser_name', 'parser_sourcelink', 'parser_script', 'parser_output']
    # CONFIGPARSER #     for option in keys:
    # CONFIGPARSER #         if parser.has_option(section, option):
    # CONFIGPARSER #             nfquerylog.debug('%s = %s' % (option, parser.get(section, option)))
    # CONFIGPARSER #         else:
    # CONFIGPARSER #             nfquerylog.debug('`%s`:`%s` option does not exists' % (section, option))
    # CONFIGPARSER #             nfquerylog.debug('Please add the option and edit the nfquery.conf file as indicated in the documentation')
    # CONFIGPARSER #             sys.exit()
    # CONFIGPARSER #     index+=1
    # CONFIGPARSER #     section = section_prefix + str(index)


    # Database Connection Start
    database = db(config_file.database.db_host, config_file.database.db_user, config_file.database.db_password, config_file.database.db_name)
    connection = database.get_database_connection()

    # Multiprocessing 
    #modules = ["querymanager", "querygenerator", "queryrepository", "scheduler"]

    #q_manager = QueryManager()
    #print config_file.parsers

    q_generator = QueryGenerator(config_file.parsers)
        
    #q_manager.start()

    # This will launch the q_generator process and execute the parsers
    q_generator.start()
    
    # Subscription Generation
    # to test subscription constructor overloading 
    # subscription1 = subscription.getInstance('name','qlist',2011)

    #subscription1 = subscription()
    #subscription1.createSubscriptionTypes()

    # Server Start
    server = SocketServer.ThreadingTCPServer((config_file.nfquery.host, config_file.nfquery.port), ThreadingTCPRequestHandler)
 
    # Activate the server; 
    # This will keep running until interrupting the server with the keyboard Ctrl-C
    try:
        nfquerylog.info('listening for plugin connections...')
        server.serve_forever()
    except KeyboardInterrupt:
        print 'keyboard Interrupt'
        # Database Connection End
        database.close_database_connection()

