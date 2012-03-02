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
        logger.LOGLEVEL = logging.DEBUG
        self.plogger = logger.createLogger('Plugin')
        self.plogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.proxy = Proxy('https://127.0.0.1:7777/')
        self.subscription_list = None
        self.reactor = reactor
        self.deferredlist = []

    def parseConfig(self, conf_file):
        self.plogger.info('In %s' % sys._getframe().f_code.co_name)
        # Parse Config File
        try:
            self.config = Config(conf_file)
        except ConfigError, e:
            print("Please check self.configuration file syntax")
            print("%s" % e)
            sys.exit(1)


    def printError(self, error):
        self.plogger.info('In %s' % sys._getframe().f_code.co_name)
        print 'error', error

    
    def shutDown(self, data):
        self.plogger.info('In %s' % sys._getframe().f_code.co_name)
        self.plogger.info("Shutting down reactor...")
        self.reactor.stop()
   

    def getSubscriptionInformation(self, subscription):
        self.plogger.info('In %s' % sys._getframe().f_code.co_name)
        self.plogger.info('getting subscription information %s' % subscription)
        return self.proxy.callRemote('get_subscription', subscription)


    def printSubscriptionDetails(self, subscription):
        self.plogger.info('In %s' % sys._getframe().f_code.co_name)
        if subscription is None:
            self.plogger.warning('Subscription info couldn\'t be gathered. Please try another subscription option : ')
        else:
            self.plogger.info('Here is the subscription information : ')
            print subscription
        self.start()
        #self.printValue(name)


    def chooseSubscription(self, value):
        self.plogger.info('In %s' % sys._getframe().f_code.co_name)
        if value is None:
            print 'we don\'t have any subscriptions yet in QueryServer ;(\n'
            raise Exception, "No Query for subscription error";
        else:
            for index in range(len(value)):
                self.plogger.info("%d  : %s " % (index, value[index]))
            while True:
                print len(value)
                self.plogger.info("Please enter your subscription number : ")
                index = raw_input()
                if index == 'q':
                    self.plogger.warning("Don want to choose a subscription, quitting.")
                    self.shutDown()
                try:
                    index = int(index)
                    if index < len(value):
                        return value[int(index)]
                    else:
                        self.plogger.error('Please enter the number in valid range or "q" for quitting.')
                except Exception, e:
                    self.plogger.error('%s' % e)
                    self.plogger.error('Please enter the number in valid range or "q" for quitting.')


    def getSubscriptionList(self, value=None):
        self.plogger.info('In %s' % sys._getframe().f_code.co_name)
        return self.proxy.callRemote('get_subscriptions')


    #def register(self):
    #    self.plogger.info('In %s' % sys._getframe().f_code.co_name)
    #    e = self.proxy.callRemote( 'register', self.config.plugin.organization, self.config.plugin.adm_name, 
    #                          self.config.plugin.adm_mail, self.config.plugin.adm_tel, self.config.plugin.adm_publickey_file, 
    #                          self.config.plugin.prefix_list, self.config.plugin.plugin_ip )
    #    e.addCallback(self.printValue)
    #    self.reactor.stop()


    def start(self):
        self.plogger.info('In %s' % sys._getframe().f_code.co_name)
        
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
        #d2 = self.chooseSubscription
        #d3 = self.getSubscription()
        #d4 = self.printSubscriptionDetails
        d1.addCallbacks(self.chooseSubscription, self.printError)
        d1.addCallback(self.getSubscriptionInformation)
        d1.addCallback(self.printSubscriptionDetails)
        #d3.addCallback(d1)
        #d1.addCallback(d1)
        #d2.addCallbacks(d3, self.printError)
        #d3.addCallbacks(d4, self.printError)
        #d4.addCallbacks(d1, self.printError)


if __name__ == "__main__":

    p = Plugin()
    p.parseConfig('./plugin.conf')
    p.start()
    try:
        p.reactor.run()
    except KeyboardInterrupt:
        print "You hit control-c"
        p.shutDown()


