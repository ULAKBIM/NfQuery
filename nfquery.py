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
from ansistrm import ColorizingStreamHandler


# List of stuff accessible to importers of this module.





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
    nfquerylog.addHandler(ColorizingStreamHandler())
    nfquerylog.debug('Starting NfQuery...')
    nfquerylog.debug('Parsing command line arguments')

    # Parse Command Line Arguments
    parser = argparse.ArgumentParser(description="Process arguments")
    parser.add_argument('conf_file', metavar="--conf", type=str, nargs='?', help='nfquery configuration file')
    args = parser.parse_args()

    # Parse Configuration File

    nffile=Config(args.conf_file)

    for section_name in parser.sections():
        print 'Section:', section_name
        print '  Options:', parser.options(section_name)
        for name, value in parser.items(section_name):
            print '  %s = %s' % (name, value)

    # Define Global Paths
    sourcepath = nffile.PATH + "/sources/amada/"
    outputpath = nffile.PATH + "/outputs/amada/"

    # Database Connection Start
    database = db(nffile.DB_HOST, nffile.DB_USER, nffile.DB_PASSWORD, nffile.DB_NAME)
    connection = database.get_database_connection()
    cursor = connection.cursor()
    cursor.close()
    database.give_database_connection()

    # Multiprocessing 
    #modules = ["querymanager", "querygenerator", "queryrepository", "scheduler"]

    #q_manager = QueryManager()
    q_generator = QueryGenerator(nffile.Parsers)
        
    #q_manager.start()

    # This will launch the q_generator process and execute the parsers
    q_generator.start()
    
    # Subscription Generation
    # to test subscription constructor overloading 
    # subscription1 = subscription.getInstance('name','qlist',2011)

    #subscription1 = subscription()
    #subscription1.createSubscriptionTypes()

    # Server Start
    server = SocketServer.ThreadingTCPServer((nffile.HOST, nffile.PORT), ThreadingTCPRequestHandler)
 
    # Activate the server; 
    # This will keep running until interrupting the server with the keyboard Ctrl-C
    try:
        nfquerylog.info('listening for plugin connections...')
        server.serve_forever()
    except KeyboardInterrupt:
        print 'keyboard Interrupt'
        # Database Connection End
        database.close_database_connection()

