#!/usr/local/bin/python

import time
import sys

from twisted.internet import reactor,defer
from txjsonrpc.web.jsonrpc import Proxy
from config import Config, ConfigError
from nfquery import logger
from termcolor import colored, cprint
from nfquery.utils import ask_yes_no
import subprocess
import logging

class Plugin:

    def __init__(self):
        logger.LOGLEVEL = logging.INFO
        #logger.LOGLEVEL = logging.DEBUG
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
            self.plogger.info('Here is the subscription information : ')
            for subscription_id, query_packets in subscription.iteritems():
                print '--------------------------------------------------------' \
                      '--------------------------------------------------------'
                print colored('SUBSCRIPTION_ID : %d' % int(subscription_id), 'cyan')
                items = query_packets.items()
                items.sort()
                query_packet_dict = [{key:value} for key, value in items]
                for qpacket in query_packet_dict:
                    for qpacket_id, query_packet in qpacket.iteritems():
                        #print colored('qpacket_id %d' % int(qpacket_id), 'white')
                        print 'QueryPacket : '
                        items = query_packet.items()
                        items.sort()
                        query_list = [{key:value} for key, value in items]
                        q_dict = {}
                        for i in range(len(query_list)):
                            for index, query in query_list[i].iteritems():
                                q_dict.update({index : query})
                                #print index, query
                                if query['category_id'] == 1:
                                    text1 = colored('    [%d] ' % int(index), 'magenta', attrs=['bold'])
                                    text2 = colored('Validation Query', 'green')
                                    print text1 + text2
                                    #print colored('\tquery_id : %d' % query['query_id'], 'white')
                                    print colored('\tfilter : %s' % query['filter'], 'white')
                                elif query['category_id'] == 2:
                                    text1 = colored('    [%d] ' % int(index), 'magenta', attrs=['bold'])
                                    text2 = colored('Mandatory Query', 'green')
                                    print text1 + text2
                                    #print '\tquery_id : ', query['query_id']
                                    print '\tfilter : ', query['filter']
                                elif query['category_id'] == 3:
                                    text1 = colored('    [%d] ' % int(index), 'magenta', attrs=['bold'])
                                    text2 = colored('Optional Query', 'green')
                                    print text1 + text2
                                    #print '\tquery_id : ', query['query_id']
                                    print '\tfilter : ', query['filter']
                        print '--------------------------------------------------------' \
                              '--------------------------------------------------------'
                        #t+=1
            #print q_dict
            text1 = '\n\tEnter the ' 
            text2 = colored('query id', 'magenta', attrs=['bold'])
            text3 = ' you want to execute :'
            #print text1 + text2 + text3
            try:
                id = int(raw_input(text1 + text2 + text3))
                for key,value in q_dict.iteritems():
                    if int(key) == id:
                        print '\n--------------------------------------------------------' \
                              '--------------------------------------------------------'
                        text = '\n\tFilter : '
                        filter = colored('\n\t\t%s ' % value['filter'], 'magenta')
                        print text + filter
                        text = colored('Do you approve the execution of filter above :', 'green')
                        answer = ask_yes_no('\n\t' + text , default="no")
                        if answer is True:
                            print colored('\tStarting Query Execution ....', 'green')
                            self.runNfDump(value['filter'])
                        else:
                            return
            except Exception, e:
                print e
                return

        #self.start()
        #self.shutDown()
        #self.printValue(name)


    def runNfDump(self, filter):
        filter = 'src net 193.140.94.0/24 and dst port 22'
        nfdump = '/usr/local/bin/nfdump'
        data = './data/nfcapd.201106211000'
        format = "fmt:srcip:%sa-srcport:%sp-dstip:%da-dstport:%dp"
        wgproc = subprocess.Popen([nfdump, '-R', data, '-o', format, filter], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (standardout, junk) = wgproc.communicate()
        output_length = len(standardout.split('\n'))
        if output_length == 6:
            print colored('\tCouldn\'t find any meaningful result', 'red')
        else:
            print colored('\tFound query execution results as given below : ', 'green')
            output = standardout.split('\n')[1:]
            output_length -= 1
            for index in range(output_length-5):
                print '\t',output[index]
            question = colored('\n\tDo you want to send statistics to NfQueryServer:', 'green')
            answer = ask_yes_no(question, default="no")
            if answer is True:
                print colored('\n\tSending statistics to NfQueryServer... ', 'green')
                self.sendStatistics('statistic')
            else:
                print colored('\tAs you wish.', 'red')
                return
            #print standardout


    def sendStatistics(self, statistics):
        pass
        return


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
                    #self.plogger.warning("Quitting.")
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
        #d1.addCallbacks(self.Test, self.printError)
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
    

