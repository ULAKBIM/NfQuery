#!/usr/local/bin/python

#import time
#from db import SingletonDatabase
#
#def printDB():
#    test1 = SingletonDatabase.getDatabaseConnection()
#    test2 = SingletonDatabase.getDatabaseConnection()
#    test3 = SingletonDatabase.getDatabaseConnection()
#    test4 = SingletonDatabase.getDatabaseConnection()
#    print "id of first connection = %s\n" % id(test1)
#    print "id of second connection = %s\n" % id(test2)
#    print "id of third connection = %s\n" % id(test3)
#    print "id of fourth connection = %s\n" % id(test4)
#    time.sleep(30)

from logger import ColoredLogger
import logging
# Start Logging Module
logging.setLoggerClass(ColoredLogger)
nfquerylog = logging.getLogger('nfquery')

logging.info('aaa')
