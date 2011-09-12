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


