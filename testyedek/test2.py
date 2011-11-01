#!/usr/local/bin/python

import sys
import time
from db import SingletonDatabase
from test import printDB

dbinstance = SingletonDatabase('localhost','nfquery','nf1!','nfquery')
print 'get main connection' 
main_con = dbinstance.getDatabaseConnection()
print dir(main_con)
main_cursor = main_con.cursor()
statement = "select query_id from query"
main_cursor.execute(statement)
query_id = main_cursor.fetchall()
for i in query_id:
    print i
print 'executing printDB\n'     
printDB()
