#!/usr/local/bin/python

import time
from db import *

test1 = Singleton('localhost','nfquery','nf1!','nfquery')
print id(test1), test1.get_id(), test1.get_connection_id()

#connection =  get_connection()
#c =  connection.cursor()
#c.execute('select 1')
#res = c.fetchall()
#print res


time.sleep(1000)



