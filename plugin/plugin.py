#!/usr/local/bin/python

import time
import sys

from twisted.internet import reactor,defer
from txjsonrpc.web.jsonrpc import Proxy
from config import Config, ConfigError
from nfquery import logger
import logging

class Plugin:

    def __init__(self):
        #logger.LOGLEVEL = logging.DEBUG
        logger.LOGLEVEL = logging.DEBUG
        self.plogger = logger.createLogger('Plugin')
        self.plogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.proxy = Proxy('https://127.0.0.1:7777/')
        #self.subscription = None
        self.chosen = None
        self.reactor = reactor

    def parseConfig(self, conf_file):
        self.plogger.debug('In %s' % sys._getframe().f_code.co_name)
        # Parse Config File
        try:
            self.config = Config(conf_file)
        except ConfigError, e:
            print("Please check self.configuration file syntax")
            print("%s" % e)
            sys.exit(1)


    def printError(self, error):
        self.plogger.debug('In %s' % sys._getframe().f_code.co_name)
        #print 'error', error
        self.shutDown()


    def shutDown(self):
        self.plogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.plogger.info("Shutting down reactor...")
        self.reactor.stop()

   
    def getSubscriptionInformation(self, subscription):
        self.plogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.plogger.info('getting subscription information %s' % subscription)
        return self.proxy.callRemote('get_subscription', subscription)


    def printSubscriptionDetails(self, subscription):
        self.plogger.debug('In %s' % sys._getframe().f_code.co_name)
        if subscription is None:
            self.plogger.warning('Subscription info couldn\'t be gathered. Please try another subscription option : ')
        else:
            self.plogger.info('Here is the subscription information : ')
            #print dir(subscription)
            print type(subscription)
            print subscription
            items = subscription.items()
            items.sort()
            sorted_subs = [value for key, value in items]
            for subs in sorted_subs:
                for category, sub in subs.iteritems():
                    print 'QueryPacket Details : '
                    if category == 'validation':
                        print category
                        print 'query_id', sub["query_id"] 
                        print 'filter', sub['filter']
                        #for key,value in sub.iteritems():
                        #    print key, value
                    else:
                        print '\tcategory', category
                        print '\tquery_id', sub[u'query_id']
                        print '\tfilter', sub[u'filter']
                    print '\n'

                   # 
                   # if category == 'validation':
                   #     # category, filter, query_id
                   #     print sub['category'] + 'query id : ' + sub['query_id'] 
                   #     print sub['filter']
                   # else:
                   #     print '\t' + sub['category'] + 'query id : ' + sub['query_id']
                   #     print '\t' + sub['filter']
                   # print '\n'
                    
        #self.start()
        #self.shutDown()
        #self.printValue(name)


    def chooseSubscription(self, value):
        self.plogger.debug('In %s' % sys._getframe().f_code.co_name)
        # value is list, either empty or not
        if (not value) or (value is None):
            self.plogger.warning('we don\'t have any subscriptions in QueryServer yet ;(')
            raise Exception, "No Query for subscription error"
        else:
            for index in range(len(value)):
                self.plogger.info("%d  : %s " % (index, value[index]))
            while True:
                print len(value)
                self.plogger.info("Please enter your subscription number : ")
                index = raw_input()
                if index == 'q':
                    self.plogger.warning("Quitting.")
                    raise Exception, 'Quitting.'
                else:
                    try:
                        index = int(index)
                        if index < len(value):
                            return value[int(index)]
                        else:
                            self.plogger.error('Please enter the number in valid range or "q" for quitting.')
                    except Exception, e:
                        self.plogger.error('%s' % e)
                        self.plogger.error('Please enter the number in valid range or "q" for quitting.')


    def getSubscriptionList(self):
        self.plogger.debug('In %s' % sys._getframe().f_code.co_name)
        return self.proxy.callRemote('get_subscriptions')

    #def register(self):
    #    self.plogger.info('In %s' % sys._getframe().f_code.co_name)
    #    e = self.proxy.callRemote( 'register', self.config.plugin.organization, self.config.plugin.adm_name, 
    #                          self.config.plugin.adm_mail, self.config.plugin.adm_tel, self.config.plugin.adm_publickey_file, 
    #                          self.config.plugin.prefix_list, self.config.plugin.plugin_ip )
    #    e.addCallback(self.printValue)
    #    self.reactor.stop()


    def start(self):
        self.plogger.debug('In %s' % sys._getframe().f_code.co_name)
        
        #####   run it reverse way ###  d1 = self.getSubscriptionList()
        #####   run it reverse way ###  #d1.addCallbacks(self.chooseSubscription, self.printError)
        #####   run it reverse way ###  d1.addCallbacks(d2, self.printError)
        #####   run it reverse way ###  d2 = self.chooseSubscription()
        #####   run it reverse way ###  #d2.addCallbacks(self.getSubscription, self.printError)
        #####   run it reverse way ###  d2.addCallbacks(d3, self.printError)
        #####   run it reverse way ###  d3 = self.getSubscription()
        #####   run it reverse way ###  #d3.addCallbacks(self.printSubscriptionDetails, self.printError)
        #####   run it reverse way ###  d3.addCallbacks(d4, self.printError)
        #####   run it reverse way ###  d4 = self.printSubscriptionDetails()
        #####   run it reverse way ###  #d4.addCallbacks(self.getSubscriptionList, self.printError)
        #####   run it reverse way ###  d4.addCallbacks(d1, self.printError)


        d1 = self.getSubscriptionList()
        d1.addCallbacks(self.chooseSubscription, self.printError)
        d1.addCallbacks(self.getSubscriptionInformation, self.printError)
        d1.addCallbacks(self.printSubscriptionDetails, self.printError)
        d1.addErrback(self.printError)

        self.reactor.callLater(1, self.start)

        #d2 = self.chooseSubscription
        #d3 = self.getSubscription()
        #d4 = self.printSubscriptionDetails
                #d1.addErrback(self.printError)
        #d3.addCallback(d1)
        #d1.addCallback(d1)
        #d2.addCallbacks(d3, self.printError)
        #d3.addCallbacks(d4, self.printError)
        #d4.addCallbacks(d1, self.printError)
 
    def run(self):
        try:
            self.reactor.run()
        except KeyboardInterrupt:
            print "You hit control-c"
            self.shutDown()



if __name__ == "__main__":

    p = Plugin()
    p.parseConfig('./plugin.conf')
    p.start()
    p.run()
    

