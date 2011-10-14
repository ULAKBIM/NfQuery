#!/usr/local/bin/python


from db import *
import time

test2 = Singleton('localhost','nfquery','nf1!','nfquery')
print id(test2), test2.get_id(), test2.get_connection_id()
time.sleep(5000)

#connection = get_connection()
#cursor = connection.cursor()
#cursor.execute('select 1')
#result=cursor.fetchall()
#print result


