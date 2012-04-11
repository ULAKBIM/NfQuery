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
        #logger.LOGLEVEL = logging.INFO
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
        #self.plogger.debug('Getting subscription information %s' % subscription)
        #return [subscription, self.proxy.callRemote('get_subscription', subscription)]
        return self.proxy.callRemote('get_subscription', subscription)


    #def printSubscriptionDetails(self, subscription_list):
    def printSubscriptionDetails(self, subscription):
        self.plogger.debug('In %s' % sys._getframe().f_code.co_name)
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        if subscription is None:
            self.plogger.warning('Subscription info couldn\'t be gathered. Please try another subscription option : ')
        else:
            #subscription_name = susbcription_list[0]
            #subscription = susbcription_list[1]
            self.plogger.info('Here is the subscription information : ')
            #print dir(subscription)
            #print type(subscription)
            #print subscription
            items = subscription.items()
            items.sort()
            s_subscription = [value for key, value in items]
            try:
                pp.pprint(s_subscription)
                for subscription_id, query_packet_dict in s_subscription[0].iteritems():
                    print '--------------------------------------------------------'
                    print 'Subscription id : ', subscription_id
                    #print 'Subscription name : ', subscription
                    query_packet_items = query_packet_dict.items()
                    query_packet_items.sort()
                    query_packet_items = [value for key, value in query_packet_items]
                    for q_packet_id, query_packet in query_packet_items[0].iteritems():
                        print '\tQueryPacket ID : ', q_packet_id
                    #    for id, query in query_packet.iteritems():
                    #        print '\t\tQuery ID    : ', query['query_id']
                    #        print '\t\t\tCategory ID : ', query['category_id']
                    #        print '\t\t\tFilter      : ', query['filter']
                        
                    #print 'QueryPacket Details :'
                    #for category, sub in sorted_subs:
                    #    if category == 'validation':
                    #        print '\t',category
                    #        print '\tquery_id', sub["query id"]
                    #        print '\tfilter', sub["filter"]
                    #        #for key,value in sub.iteritems():
                    #        #    print key, value
                    #    else:
                    #        print '\t\tcategory', category
                    #        print '\t\tquery_id', sub['query id']
                    #        print '\t\tfilter', sub['filter']
                    #    print '\n'
            except Exception, e:
                self.plogger.warning(e)
                #return

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
            self.plogger.info("Here is the subscription types.")
            #print "- Here is the subscription types."
            #print value
            for index in range(len(value)):
                #self.plogger.info("%d  : %s " % (index, value[index]))
                print "\t%d\t:\t%s " % (index, value[index])
            print "\tq/Q\t:\tQUIT"
            while True:
                #self.plogger.info("Please enter the subscription number you want to use")
                print "Please enter the subscription number you want to use : "
                index = raw_input()
                if index == 'q' or index == 'Q':
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

        # recursive call of self.start
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
    

