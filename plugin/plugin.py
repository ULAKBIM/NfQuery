#!/usr/local/bin/python

import subprocess
import logging
import locale
import time
import sys

from twisted.internet import reactor,defer
from txjsonrpc.web.jsonrpc import Proxy
from config import Config, ConfigError
from nfquery import logger
from termcolor import colored, cprint
from nfquery.utils import ask_yes_no, addressInNetwork


class Plugin:

    def __init__(self):
        logger.LOGLEVEL = logging.INFO
        #logger.LOGLEVEL = logging.DEBUG
        self.plogger = logger.createLogger('Plugin')
        self.plogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.proxy = Proxy('https://193.140.94.205:7777/')
        #self.subscription = None
        self.chosen = None
        self.prefix_list = None
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
        try:
            self.shutDown()
            return
        except Exception, e:
            #print("%s" % e)
            sys.exit()


    def shutDown(self):
        self.plogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.plogger.warning("Shutting down reactor...")
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
                        filter = colored('\n\t\t%s ' % value['filter'], 'magenta', attrs=['bold'])
                        print text + filter
                        text = colored('Do you approve the execution of filter above :', 'green')
                        answer = ask_yes_no('\n\t' + text , default="no")
                        if answer is True:
                            print colored('\tStarting Query Execution ....', 'green')
                            self.runNfDump(value['filter'], type=1)
                            print '\n--------------------------------------------------------' \
                                  '--------------------------------------------------------\n'
                        else:
                            return
            except Exception, e:
                print e
                return


    def format_num(self, num):
        locale.setlocale(locale.LC_NUMERIC, "")
        """
            Format a number according to given places.
            Adds commas, etc. Will truncate floats into ints!
        """
        try:
            inum = int(num)
            return locale.format("%.*f", (0, inum), True)

        except (ValueError, TypeError):
            return str(num)


    def get_max_width(self, table, index):
        """
            Get the maximum width of the given column index
        """
        return max([len(self.format_num(row[index])) for row in table])


    def pprint_table(self, out, table):
        """
            Prints out a table of data, padded for alignment
            @param out: Output stream (file-like object)
            @param table: The table to print. A list of lists.
            Each row must have the same number of columns. 
        """

        col_paddings = []

        for i in range(len(table[0])):
            col_paddings.append(self.get_max_width(table, i))

        for row in table:
            # left col
            print >> out, row[0].ljust(col_paddings[0] + 1),
            # rest of the cols
            for i in range(1, len(row)):
                col = self.format_num(row[i]).rjust(col_paddings[i] + 1)
                print >> out, col,
            print >> out


    def runNfDump(self, filter, type=1):
        import string
        #filter = 'src ip 193.140.94.140 and dst port 123'
        nfdump = '/usr/local/bin/nfdump'
        data = './demoflow/'
        #data = './data/'
        format = "fmt:srcip:%sa-srcport:%sp-dstip:%da-dstport:%dp"
        #aggregate = "srcip,dstip,dstport"
        aggregate = "dstip"
        wgproc = subprocess.Popen([nfdump, '-R', data, '-o', format, '-A', aggregate, filter], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (standardout, junk) = wgproc.communicate()
        output_length = len(standardout.split('\n'))
        if output_length == 6:
            print colored('\tCouldn\'t find any meaningful result', 'green')
        else:
            print colored('\tFound query execution results as given below : \n', 'green')
            output = standardout.split('\n')[1:]
            output_length -= 1
            #key_list = []
            fields = ["\tsrcip", "srcport", "dstip", "dstport"]
            for i in range(len(fields)):
                fields[i] = colored(fields[i], 'magenta', attrs=['bold'])
            print_table = [fields]
            table = []
            for index in range(output_length-5):
                out = output[index].replace(" ","").split('-')
                l_print = []
                l_all = []
                for o in out:
                    #print o
                    #if o.split(':')[0] == 'srcip':
                    #    l_print.append(colored('\t' + o.split(':')[1], 'white', attrs=['bold']))
                    #    l_all(o.split(':')[1])
                    #elif o.split(':')[0] == 'srcport':
                    #    l_print.append(colored(o.split(':')[1], 'white', attrs=['bold']))
                    #elif o.split(':')[0] == 'dstip':
                    #    l_print.append(colored(o.split(':')[1], 'white', attrs=['bold']))
                    #elif o.split(':')[0] == 'dstport':
                    #    l_print.append(colored(o.split(':')[1], 'white', attrs=['bold']))
                    #else:
                    #    print 'pat'
                    l_print.append(colored('\t' + o.split(':')[1], 'white', attrs=['bold']))
                    l_all.append(o.split(':')[1])
                print_table.append(l_print)
                table.append(l_all)
            #print len(table)
            #print table

            for index in range(len(table)-1):
                for prefix in self.prefix_list:
                    flag1 = addressInNetwork(table[index][0], prefix)
                    flag2 = addressInNetwork(table[index][2], prefix)
                    print colored(' -------------- found2 -----------', 'red', attrs=['bold'])
                    print prefix
                    print table[index][2]

            self.pprint_table(sys.stdout, print_table)
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


    def register(self):
        self.plogger.info('In %s' % sys._getframe().f_code.co_name)
        call = self.proxy.callRemote( 'register', self.config.plugin.organization, 
                                               self.config.plugin.adm_name,
                                               self.config.plugin.adm_mail, 
                                               self.config.plugin.adm_tel, 
                                               self.config.plugin.adm_publickey_file,
                                               self.config.plugin.prefix_list, 
                                               self.config.plugin.plugin_ip )
        call.addCallback(self.printValue)
        

    def printValue(self, return_value):
        self.plogger.info('In %s' % sys._getframe().f_code.co_name)
        print '--------------------------------------------------------' \
              '--------------------------------------------------------'
        self.plogger.info(colored(return_value, 'green', attrs=['bold']))
        print '--------------------------------------------------------' \
              '--------------------------------------------------------'


    def getPrefixes(self):
        self.plogger.debug('In %s' % sys._getframe().f_code.co_name)
        call = self.proxy.callRemote( 'get_prefixes', self.proxy.host)
        call.addCallback(self.assignPrefixList)


    def assignPrefixList(self, prefix_list):
        self.plogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.prefix_list = prefix_list
        self.plogger.info(self.prefix_list)
        

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
        d1.addCallbacks(self.chooseSubscription)
        d1.addCallbacks(self.getSubscriptionInformation)
        d1.addCallbacks(self.printSubscriptionDetails)
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
            sys.exit()
            #self.shutDown()



if __name__ == "__main__":

    p = Plugin()
    p.parseConfig('./plugin.conf')
    p.register()
    p.getPrefixes()
    p.start()
    p.run()
    

