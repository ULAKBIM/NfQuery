#!/usr/local/bin/python

import simplejson 
import MySQLdb

# nfquery imports
from test.query import query

def connectDB():
    # Open database connection
    db = MySQLdb.connect("localhost","nfquery","nf1!","ulaknet" )
    db = connectDB()
    cursor = db.cursor()
    # Fetch a single row using fetchone() method.
                                                  
    cursor.close()    
    db.close()
    # return db object for using outside 
    #return db
    
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



def create_query(source_name, source_desc, source_link, threat_type, threat_name, output_type, output, creation_time):
    '''
      Get query information from parser and pass to the Query Generator.
    '''
    myquery = query(source_name, source_desc, source_link, threat_type, threat_name, output_type, output, creation_time)
    myquery.insert_query() 
    myquery.print_content()
