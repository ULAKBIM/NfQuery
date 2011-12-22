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
#from ansistrm import ColorizingStreamHandler

# ------------------------------------------------------------------------------------- #
class nfquery(multiprocessing.Process):
    def run():
        pass

class globals:
    
    #path = "/usr/local/nfquery"
    path = "/home/serdar/nfquery"
    parsers_path = path + "/parsers"

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

    # Parse Config File
    config_file = Config(args.config_file)

    # Start Database Connection
    database = db(config_file.database.db_host, config_file.database.db_user, config_file.database.db_password, config_file.database.db_name)
    connection = database.get_database_connection()

    nfquery_globals.path = config_file.nfquery.path
    nfquery_globals.parsers_path = config_file.nfquery.parsers_path

    # Start Query Generator
    q_generator = QueryGenerator(config_file.parsers)
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

