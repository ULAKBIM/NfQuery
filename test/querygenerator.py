#!/usr/local/bin/python

import simplejson 

from query import Query

import MySQLdb

def connectDB():
    # Open database connection
    db = MySQLdb.connect("localhost","nfquery","nf1!","ulaknet" )
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    # execute SQL query using execute() method.
    cursor.execute("SELECT VERSION()")
    # Fetch a single row using fetchone() method.
    data = cursor.fetchone()
    print "Database version : %s " % data
    db.close()    
    
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


def generateQuery(source_name, threat_type, threat_desc, creation_time, ip=None, domain=None, port=None):
    # it could be only port information
    if (ip is None) and (domain is None) and (port is None):
        sys.exit("both ip,domain and port can not be EMPTY or None at the same time\nyou have to set at least one of them\n")
    if (port is not None):
        # Insert information into query table
        ################
        ################
        ################
        ################
        ################
        ################
        ################
        ################
        print 'port'
    else:
        # Insert information into query table
        nfquery.connectDB("localhost","nfquery","nf1!","nfquery")
    
    
    
        




















