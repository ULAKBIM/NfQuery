#!/usr/local/bin/python 


from twisted.internet.threads import deferToThread
from twisted.internet.defer import gatherResults
from twisted.internet import reactor

def double(n):
    print n * 2

data = [1, 2, 3, 4]

results = []
for datum in data:
    deferToThread(double, datum)


d = gatherResults(results)
def displayResults(results):
    print 'Doubled data:', results
d.addCallback(displayResults)
#d.addCallback(lambda ignored: reactor.stop())

reactor.run()

