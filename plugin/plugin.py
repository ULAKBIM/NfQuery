#!/usr/local/bin/python

import subprocess
import logging
import locale
import time
import sys
import string

from twisted.internet import reactor,defer
from txjsonrpc.web.jsonrpc import Proxy
from config import Config, ConfigError
from nfquery import logger
from termcolor import colored
from nfquery.utils import ask_yes_no, addressInNetwork
from datetime import datetime


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
                        text = '\tFilter : '
                        filter = colored('\n\t\t%s ' % value['filter'], 'magenta', attrs=['bold'])
                        print text + filter
                        text = colored('Do you approve the execution of filter above :', 'green')
                        answer = ask_yes_no('\n\t' + text, default="no")
                        if answer is True:
                            print colored('\tStarting Query Execution ....', 'green')
                            #print dir(value)
                            #pp.pprint(value)
                            self.runNfDump(value['filter'], type=value['query_type'], index=id)
                            print '\n--------------------------------------------------------' \
                                  '--------------------------------------------------------\n'
                        else:
                            return
            except Exception, e:
                print e
                return

    '''
        SUBSCRIPTION_ID : 49

        QueryPacket : 

            [0] Validation Query
                filter : src ip 193.140.94.160  and src port 41315  and dst ip 193.140.83.122  and dst port 4101 

            [1] Mandatory Query
                filter :  src ip 193.140.94.160  and dst port 4101 

            [2] Optional Query
                filter :  src ip 193.140.94.160  and dst ip 193.140.83.122  and dst port 4101 

            [3] Optional Query
                filter :  src ip 193.140.94.160  and src port 41315  and dst port 4101

    '''


    def runNfDump(self, filter, type='', index=0):
        #print 'here6'
        # This works without errors only for the honeypot demo use-case scenario
        # Try to find a generic way for analyzing flows according to queries.
        nfdump = '/usr/local/bin/nfdump'
        data = './demoflow/'
        format = "fmt:srcip:%sa-srcport:%sp-dstip:%da-dstport:%dp"
        filter = filter
        index = index
        type_list = ['srcip', 'srcport', 'dstip', 'dstport']
        type = type.split(',')

        if  index == 0:       # means it's validation query

            '''
                [0] Validation Query
                    filter : src ip 193.140.94.160  and src port 41315  and dst ip 193.140.83.122  and dst port 4101
            '''


            aggregate = "srcip,srcport,dstip,dstport"

            #wgproc = subprocess.Popen([nfdump, '-R', data, '-o', format, '-A', aggregate, filter], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            #(standardout, junk) = wgproc.communicate()

        elif  index == 1:     # means it's mandatory query

            '''
                [1] Mandatory Query
                    filter :  src ip 193.140.94.160  and dst port 4101
            '''

            # Format Determination
            #   * Output format should include only the fields we need to correlate
            #   * So, for mandatory and optional queries, we don't include filter fields
            #     in the output format.
            #   * Additionally, for now, we won't include srcport, because we never need it.


            # Aggregation Determination
            #   * Generally, the complement fields of what is given as filter fields
            #     is used as aggreagation fields. Because we already know what is given,
            #     and we need to correlate extracted output. 
            #   * Also, We don't use srcport here as we don't use it in output format.

            #print type_list
            removal_list1=[]
            #removal_list2=[]
            for t in type:
                removal_list1.append(type_list[int(t)])
                #removal_list2.append(format_list[int(t)])

            for removal in removal_list1:
                for t in type_list:
                    if removal == t:
                        type_list.remove(removal)

            # Lastly remove srcport
            #print type_list.remove('srcport')

            #print type_list

            '''
                determining the aggregation 
            '''

            aggregate = ""
            length = len(type_list)
            #print length
            for i in range(length-1):
                aggregate += type_list[i]
            #print 'ok'
            #aggregate += type_list[length-1]
            aggregate = "srcip,dstip,dstport"
            #print type_list[length-1]
            #print 'aggregate', aggregate
            #print 'format', format
            wgproc = subprocess.Popen([nfdump, '-R', data, '-o', format, '-A', aggregate, filter], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            (standardout, junk) = wgproc.communicate()
            output_length = len(standardout.split('\n'))
            if output_length == 6:
                print colored('\tCouldn\'t find any meaningful result', 'green')
                return
            else:
                print colored('\tQuery execution result is given below : \n', 'green')
                output = standardout.split('\n')[1:output_length-5]
                #print output

            fields = ["\tsrcip", "srcport", "dstip", "\t\tdstport"]
            for i in range(len(fields)):
                fields[i] = colored(fields[i], 'magenta', attrs=['bold'])
            print_table = [fields]
            table = []
            for index in range(output_length-6):
                #print output[index]
                out = output[index].replace(" ","").split('-')
                l_print = []
                l_all = []
                for o in out:
                    l_print.append(colored('\t' + o.split(':')[1], 'white', attrs=['bold']))
                    l_all.append(o.split(':')[1])
                print_table.append(l_print)
                table.append(l_all)
            #print len(table)
            self.pprint_table(sys.stdout, print_table)
            print '\n'

            # We should remove this for demo.
            self.prefix_list.remove('193.140.83.0/24')

            new_query_list = []
            expr_list = []
            print '\n--------------------------------------------------------' \
                    '--------------------------------------------------------\n'
            for prefix in self.prefix_list:
                for index in range(len(table)):
                    flag = addressInNetwork(table[index][2], prefix)
                    if flag:
                        print colored(('\tFound : %s in prefix %s' % (table[index][2], prefix)), 'green', attrs=['bold'])
                        expr_list.append( 
                                           {
                                            "src_ip"   : str(table[index][0]),
                                            "dst_ip"   : str(table[index][2]),
                                            "dst_port" : str(table[index][3])
                                           }
                                         )
            creation_time = time.strftime('%Y-%m-%d %H:%M')
            #print creation_time
            #print type(creation_time)
            #print 'hee'
            
            #-------------------------------------------#
            alert = [
                        {
                         "expr_list" : expr_list,
                         "mandatory_keys" : ["src_ip","dst_port"],
                         "source_id" : 13,
                         "date" : creation_time,
                         "prefix" : prefix,
                        }
                    ]
            #print alert
            #-------------------------------------------#
            print '\n--------------------------------------------------------' \
                  '--------------------------------------------------------\n'

            question = colored('\n\tDo you want to send statistics to NfQueryServer:', 'green')
            answer = ask_yes_no(question, default="no")
            if answer is True:
                print colored('\n\tSending statistics to NfQueryServer... ', 'green')
                try:
                    call = self.proxy.callRemote('get_alert', alert)
                    call.addCallback(self.printValue)
                except Exception,e:
                    print e
            else:
                print colored('\tAs you wish.', 'red')
                return
        else:                 # means it's optional query
 
            '''
                [2] Optional Query
                    filter :  src ip 193.140.94.160  and dst ip 193.140.83.122  and dst port 4101    
            ''' 

            print 'doing nothing'

            #wgproc = subprocess.Popen([nfdump, '-R', data, '-o', format, '-A', aggregate, filter], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            #(standardout, junk) = wgproc.communicate()


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
        self.plogger.debug('In %s' % sys._getframe().f_code.co_name)
        print colored(str(return_value), 'green', attrs=['bold'])
        print '--------------------------------------------------------' \
              '--------------------------------------------------------'


    def getPrefixes(self):
        self.plogger.debug('In %s' % sys._getframe().f_code.co_name)
        call = self.proxy.callRemote( 'get_prefixes', self.proxy.host)
        call.addCallback(self.assignPrefixList)


    def getAlerts(self):
        self.plogger.debug('In %s' % sys._getframe().f_code.co_name)
        # get with ip
        #call = self.proxy.callRemote( 'get_alerts', self.proxy.host)
        # get with prefix
        call = self.proxy.callRemote( 'get_my_alerts', self.proxy.host)
        call.addCallback(self.printAlerts)


    def printAlerts(self, return_value):
        self.plogger.debug('In %s' % sys._getframe().f_code.co_name)
        if return_value:
            for alert in return_value:
                print colored('\t' + str(alert), 'green', attrs=['magenta'])
            print '--------------------------------------------------------' \
                  '--------------------------------------------------------'
        else:
            print 'No alert exists for your plugin.'
        print '\n\n'


    def assignPrefixList(self, prefix_list):
        self.plogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.prefix_list = prefix_list
        #self.plogger.info(self.prefix_list)
        

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
    p.getAlerts()
    p.start()
    p.run()
    

