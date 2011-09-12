#!/usr/local/bin/python

import simplejson 
from query import Query

q=Query(1, "amada", "FAKE-AV", "27.03.1990", ip="193.140.94.94").__dict__
queryfile = open('outputs/test.jason', mode='w')
queryfile.writelines(simplejson.dumps(q, indent=4)+"\n")
queryfile.write(simplejson.dumps(q, indent=4))
queryfile.write(simplejson.dumps(q, indent=4))
queryfile.close()

#anotherfile=open('test.jason', mode='r')
#loaded = simplejson.load(anotherfile)
#print loaded


#!/usr/local/bin/python

import MySQLdb

# Open database connection
db = MySQLdb.connect("localhost","nfquery","nf1!","ulaknet" )

# prepare a cursor object using cursor() method
cursor = db.cursor()

# execute SQL query using execute() method.
cursor.execute("SELECT VERSION()")

# Fetch a single row using fetchone() method.
data = cursor.fetchone()

print "Database version : %s " % data

# disconnect from server
db.close()

