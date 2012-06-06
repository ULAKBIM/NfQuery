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
        #self.proxy = Proxy('http://193.140.94.205:7777/')
        #self.proxy = Proxy('https://193.140.94.205:7777/', version=2)
        #self.proxy = Proxy('http://193.140.94.205:7777/', version=2)
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
            #self.shutdown()
            return


    def shutDown(self):
        self.plogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.plogger.warning("Shutting down reactor...")
        if reactor.running:
            self.reactor.stop()
        else:
            return

   
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
                            time.sleep(1)
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
        data = './flow/demoflow/'
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
            # COMMENTED FOR DEMO # wgproc = subprocess.Popen([nfdump, '-R', data, '-o', format, '-A', aggregate, filter], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # COMMENTED FOR DEMO # (standardout, junk) = wgproc.communicate()


            # COMMENTED FOR DEMO # output_length = len(standardout.split('\n'))
            # COMMENTED FOR DEMO # if output_length == 6:
            # COMMENTED FOR DEMO #     print colored('\tCouldn\'t find any meaningful result', 'green')
            # COMMENTED FOR DEMO #     return
            # COMMENTED FOR DEMO # else:
            # COMMENTED FOR DEMO #     print colored('\tQuery execution result is given below : \n', 'green')

            # demo part #####################################
            print "\n"
            fields  = "\tsrcip\t\tsrcport\t\tdstip\t\tdstport"
            print colored(fields, 'magenta', attrs=['bold'])
            print colored("\t192.168.0.160\t0\t\t10.10.0.122\t4101", 'blue', attrs=['bold'])
            print colored("\t192.168.0.160\t0\t\t172.16.0.2\t4101", 'blue', attrs=['bold'])
            print colored("\t192.168.0.160\t0\t\t172.16.0.10\t4101", 'blue', attrs=['bold'])
            # demo part #####################################

            # COMMENTED FOR DEMO #     output = standardout.split('\n')[1:output_length-5]
            # COMMENTED FOR DEMO #     #print output

            # COMMENTED FOR DEMO # fields = ["\tsrcip", "srcport", "dstip", "\t\tdstport"]
            # COMMENTED FOR DEMO # for i in range(len(fields)):
            # COMMENTED FOR DEMO #     fields[i] = colored(fields[i], 'magenta', attrs=['bold'])
            # COMMENTED FOR DEMO # print_table = [fields]
            # COMMENTED FOR DEMO # table = []
            # COMMENTED FOR DEMO # for index in range(output_length-6):
            # COMMENTED FOR DEMO #     #print output[index]
            # COMMENTED FOR DEMO #     out = output[index].replace(" ","").split('-')
            # COMMENTED FOR DEMO #     l_print = []
            # COMMENTED FOR DEMO #     l_all = []
            # COMMENTED FOR DEMO #     for o in out:
            # COMMENTED FOR DEMO #         l_print.append(colored('\t' + o.split(':')[1], 'blue', attrs=['bold']))
            # COMMENTED FOR DEMO #         l_all.append(o.split(':')[1])
            # COMMENTED FOR DEMO #     print_table.append(l_print)
            # COMMENTED FOR DEMO #     table.append(l_all)
            # COMMENTED FOR DEMO # #print len(table)
            # COMMENTED FOR DEMO # self.pprint_table(sys.stdout, print_table)
            # COMMENTED FOR DEMO # print '\n'

            # COMMENTED FOR DEMO # # We should remove this for demo.
            # COMMENTED FOR DEMO # self.prefix_list.remove('193.140.83.0/24')

            new_query_list = []
            expr_list = []
            print '\n--------------------------------------------------------' \
                    '--------------------------------------------------------\n'
            # COMMENTED FOR DEMO # for prefix in self.prefix_list:
            # COMMENTED FOR DEMO #     for index in range(len(table)):
            # COMMENTED FOR DEMO #         flag = addressInNetwork(table[index][2], prefix)
            # COMMENTED FOR DEMO #         if flag:
            # COMMENTED FOR DEMO #             print colored(('\tFound : %s in prefix %s' % (table[index][2], prefix)), 'green', attrs=['bold'])
            # COMMENTED FOR DEMO #             expr_list.append( 
            # COMMENTED FOR DEMO #                                {
            # COMMENTED FOR DEMO #                                 "src_ip"   : str(table[index][0]),
            # COMMENTED FOR DEMO #                                 "dst_ip"   : str(table[index][2]),
            # COMMENTED FOR DEMO #                                 "dst_port" : str(table[index][3])
            # COMMENTED FOR DEMO #                                }
            # COMMENTED FOR DEMO #                              )
            # COMMENTED FOR DEMO # creation_time = time.strftime('%Y-%m-%d %H:%M')
            #print creation_time
            #print type(creation_time)
            #print 'hee'

            # demo part ##########################
            print colored('\tFound : 10.10.0.122 in prefix 10.10.0.0/24', 'green', attrs=['bold'])
            print colored('\tFound : 172.16.0.2 in prefix 172.16.0.0/24', 'green', attrs=['bold'])

            
            #-------------------------------------------#
            # COMMENTED FOR DEMO # alert = [
            # COMMENTED FOR DEMO #             {
            # COMMENTED FOR DEMO #              "expr_list" : expr_list,
            # COMMENTED FOR DEMO #              "mandatory_keys" : ["src_ip","dst_port"],
            # COMMENTED FOR DEMO #              "source_id" : 13,
            # COMMENTED FOR DEMO #              "date" : creation_time,
            # COMMENTED FOR DEMO #              "prefix" : prefix,
            # COMMENTED FOR DEMO #             }
            # COMMENTED FOR DEMO #         ]
            #print alert
            #-------------------------------------------#
            print '\n--------------------------------------------------------' \
                  '--------------------------------------------------------\n'

            #question = colored('\n\tDo you want to send statistics to NfQueryServer:', 'green')
            #answer = ask_yes_no(question, default="no")
            # COMMENTED # if answer is True:
            # COMMENTED #     print colored('\n\tSending statistics to NfQueryServer... ', 'green')
            print colored('\n\tSending statistics to NfQueryServer... ', 'green')
            time.sleep(20)
                ###### COMMENTED FOR DEMO # try:
                ###### COMMENTED FOR DEMO #     # COMMENTED FOR DEMO # call = self.proxy.callRemote('get_alert', alert)
                ###### COMMENTED FOR DEMO #     ###################### call.addCallback(self.printValue)
                ###### COMMENTED FOR DEMO # except Exception,e:
                ###### COMMENTED FOR DEMO #     print e
            # COMMENTED # else:
            # COMMENTED #     print colored('\tAs you wish.', 'red')
            # COMMENTED #     return
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
        call = self.proxy.callRemote( 'register', 
                                      self.config.plugin.organization, 
                                      self.config.plugin.adm_name,
                                      self.config.plugin.adm_mail, 
                                      self.config.plugin.adm_tel, 
                                      self.config.plugin.adm_publickey_file,
                                      self.config.plugin.prefix_list, 
                                      self.config.plugin.plugin_ip )
        #call.addCallback(self.printValue)
        

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
        d1.addCallbacks(self.chooseSubscription,self.printError)
        d1.addCallbacks(self.getSubscriptionInformation,self.printError)
        d1.addCallbacks(self.printSubscriptionDetails,self.printError)
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
    p.parseConfig('./plugin.conf.py')
    p.register()
    p.getPrefixes()
    #p.getAlerts()
    p.start()
    p.run()
    

