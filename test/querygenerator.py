#!/usr/local/bin/python

import simplejson 

from query import Query

import MySQLdb

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


def generateQuery(query):
    # it could be only port information
    if (query.ip is None) and (query.domain is None) and (query.port is None):
        sys.exit("both ip,domain and port can not be EMPTY or None at the same time\nyou have to set at least one of them\n")
    if (query.port is not None):
        print 'port'
    else:
            
        
        

        
        


q = Query("a","b","c","d",ip="192.168.7.6")
generateQuery(q)
        


    
    
    
        




















