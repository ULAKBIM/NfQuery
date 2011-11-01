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

# List of stuff accessible to importers of this module.

#q=Query(1, "amada", "FAKE-AV", "27.03.1990", ip="193.140.94.94").__dict__
#queryfile = open('outputs/test.jason', mode='w')
#queryfile.writelines(simplejson.dumps(q, indent=4)+"\n")
#queryfile.write(simplejson.dumps(q, indent=4))
#queryfile.write(simplejson.dumps(q, indent=4))
#queryfile.close()
#
#anotherfile=open('test.jason', mode='r')

#loaded = simplejson.load(anotherfile)
#print loaded


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
    multiprocessing.log_to_stderr(logging.DEBUG)
    # Parse Command Line Arguments
    parser = argparse.ArgumentParser(description="Process arguments")
    parser.add_argument('conf_file', metavar="--conf", type=str, nargs='?', help='nfquery configuration file')
    args = parser.parse_args()

    # Parse Configuration File
    nffile=Config(args.conf_file)

    # Define Global Paths
    sourcepath = nffile.PATH + "/sources/amada/"
    outputpath = nffile.PATH + "/outputs/amada/"

    # Database Connection Start
    try:
        database = db(nffile.DB_HOST, nffile.DB_USER, nffile.DB_PASSWORD, nffile.DB_NAME)
        connection = database.get_connection()
        cursor = connection.cursor()
    except MySQLdb.Error, e:
        sys.exit ("Error %d: %s" % (e.args[0], e.args[1]))

    # Multiprocessing 
    modules = ["querymanager", "querygenerator", "queryrepository", "scheduler"]

    #q_manager = QueryManager()
    q_generator = QueryGenerator(cursor, nffile.Parsers)
        
    #q_manager.start()
    q_generator.start()
    
    # Subscription Generation
    #subscription_list = generateSourceSubscriptionPackets(1, cursor1, cursor2)
    #for i in subscription_list:
    #    print i.__dict__


    # Server Start
    server = SocketServer.ThreadingTCPServer((nffile.HOST, nffile.PORT), ThreadingTCPRequestHandler)
 
    # Activate the server; 
    # This will keep running until interrupting the server with the keyboard Ctrl-C
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print 'keyboard Interrupt'
        # Database Connection End
        database.end_connection()

