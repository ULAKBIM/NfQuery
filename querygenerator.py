#!/usr/local/bin/python

import simplejson 
import logging
import multiprocessing
import sys
# useful but necessary?
import pprint


# nfquery imports
from query import query
from subscription import subscription
from db import db


    # --------------------------- JSON TEST -----------------------------------#
    #q=Query(1, "amada", "FAKE-AV", "27.03.1990", ip="193.140.94.94").__dict__ #
    #queryfile = open('outputs/test.jason', mode='w')                          #
    #queryfile.writelines(simplejson.dumps(q, indent=4)+"\n")                  #
    #queryfile.write(simplejson.dumps(q, indent=4))                            #
    #queryfile.write(simplejson.dumps(q, indent=4))                            #
    #queryfile.close()                                                         #
    #                                                                          #
    #anotherfile=open('test.jason', mode='r')                                  #
    #                                                                          #
    #loaded = simplejson.load(anotherfile)                                     #
    #print loaded                                                              #
    # --------------------------- JSON TEST -----------------------------------#
    

__all__ = ['create_query', 'QueryGenerator']

class QueryGenerator(multiprocessing.Process):

    #def __init__(self, subscription_name, subscription_query_list, subscription_update_time):
    #    self.subscription_name = subscription_name
    #    self.subscription_query_list = subscription_query_list
    #    self.subscription_update_time = subscription_update_time
   
    # buna bi cozum bulmak lazim boyle lok diye tanimlamayalim, global degiskenlerin oldugu bir listemiz olsun
    # ya da dictionary, ordan cagiralim
    parser_path = '/home/serdar/nfquery/parsers'

    def __init__(self, parsers):
        multiprocessing.Process.__init__(self)
        self.parsers = parsers
        connection = db.get_database_connection()
        self.cursor = connection.cursor()
        logging.basicConfig(level=logging.INFO)
        self.qglogger = logging.getLogger('QueryGenerator')
        self.qglogger.setLevel(logging.INFO)

    def run(self):
        self.checkParsers(self.parsers.split(','))
        #self.executeParsers()
        self.generateSubscriptionPackets()


    def executeParsers(self):
        if not self.parsers:
            sys.exit('No parser is found, please check your nfquery.conf file!')
        else:
            parser_list = self.parsers.split(',')
        if(self.checkParsers(parser_list)):
            print 'Parsers are OK, Lets start executing each parser.'
            from parsers.amadaParser import fetch_source, parse_source
            #source_link = "http://amada.abuse.ch/blocklist.php?download=ipblocklist"
            fetch_source('http://amada.abuse.ch/blocklist.php?download=ipblocklist')
            #source_file = nfquery + sourcepath + "blocklist"
            source_file = "/usr/local/nfquery/" + "sources/amada/" + "blocklist"
            parse_source(source_file)
            #print locals()
        else:
            sys.exit('You do something wrong with the parser names.')


    def checkParsers(self, parser_list):
        self.qglogger.info('In %s' % self.name)
        # fetch registered parser names FROM the database and check them with existing parser file names.
        statement = 'SELECT parser_desc FROM parser'
        self.cursor.execute(statement)
        registered_parsers = self.cursor.fetchall()
        parsers = ()
        
        # Convert 'tuple of tuples' to 'a single tuple'
        for (p,) in registered_parsers:
            parsers = parsers + (p,)
        
        # Check for each parser, if it is registered.
        for parser in parser_list:
            if parser in parsers:
                self.qglogger.info('Parser  "%s" Exists, OK!' % parser)
            else:
                return 0
                #sys.exit('Parser doesn\'t exist, NOT!')
        return 1


    def generateSubscriptionPackets(self):
        self.qglogger.info('In %s' % self.name)
        '''
           Starts the parsers, generates queries and passes to query manager for releasing.
        '''
        statement = 'SELECT source_id FROM source'
        self.cursor.execute(statement)
        registered_sources = self.cursor.fetchall()
        print 'Generating Subscriptions...'
        for (source_id,) in registered_sources:
            self.generateSourceSubscriptionPackets(source_id)
        self.generateThreatNameSubscriptions()
        self.generateSourceThreatTypeSubscriptions()
   

    def generateSourceSubscriptionPackets(self, source_id):
        try:
            self.qglogger.info('In %s' % self.name)
            statement = """SELECT source_name FROM source WHERE source_id=%d""" % (source_id)
            self.cursor.execute(statement)
            source_name = self.cursor.fetchone()
            if not source_name:
                sys.exit("There is no source registered in the database with this name.") 
            statement = """SELECT query_id FROM query WHERE source_id=%d""" % (source_id)
            self.cursor.execute(statement)
            query_id = self.cursor.fetchall()
            #print query_id
            if not query_id:
                self.qglogger.debug("We don't have any query for this source.")
                self.qglogger.info("No query is available for %s subscription." % (source_name) )
            else:
                for qid in query_id:
                    statement = ( """SELECT subscription_query.query_id FROM subscription,subscription_query """ + 
                                  """WHERE subscription.subscription_desc='%s' """ % (source_name) + 
                                  """AND subscription.subscription_id=subscription_query.subscription_id"""
                                )
                    #print statement
                    self.cursor.execute(statement)
                    query_id_list = self.cursor.fetchall()
                    if query_id_list:
                        subscription_list = []
                        subscription_list.append(subscription(source_name, query_id_list, '2011'))
                        ###### gather subscription information #####   
                        #for (query_id,) in query_id_list:
                        #    self.cursor.execute(""" SELECT ip.ip FROM query,query_ip,ip WHERE query.query_id=%s and query.query_id=query_ip.query_id and query_ip.ip_id=ip.ip_id""", (query_id))
                        #    ip_list = self.cursor.fetchall()
                        #    # subscription_desc, subs
                        #    # Generate the subscription object
                        ############################################
                for i in subscription_list:
                    print "source subscription packets for %s --> %s" % (source_name, i.__dict__)
                return subscription_list   
        except Exception, e:
            sys.exit ("Error %s" % (e.args[0]))
            return 0



    def generateThreatNameSubscriptions(self, threat_id=None):
        self.qglogger.info('In %s' % self.name)
        print 'generateThreatNameSubscriptionPackets'
        try:
            statement = """SELECT threat_id FROM threat WHERE threat_name<>'NULL' GROUP BY threat_name"""
            self.cursor.execute(statement)
            subscription_list = []
            for threat_id in self.cursor.fetchall():
                print threat_id
                statement = """SELECT query_id FROM query WHERE threat_id=%s""" % threat_id
                self.cursor.execute(statement)
                query_id_list = self.cursor.fetchall()
                if not query_id_list:
                    self.qglogger.info("No query is available for %d subscription." % (threat_id) )
                else:
                    subscription_list.append(subscription(threat_id, query_id_list, '2011'))
            for i in subscription_list:
                print "threat name subscription packets for %s --> %s" % (threat_id, i.__dict__)
        except Exception, e:
            sys.exit ("Error %s" % (e.args[0]))
            return 0



    def generateThreatTypeSubscriptions(self, threat_type=None):
        self.qglogger.info('In %s' % self.name)
        print 'generateThreatTypeSubscriptionPackets'
        try:
            statement = """SELECT threat_type FROM threat GROUP BY threat_type"""
            self.cursor.execute(statement)
            for threat_type in self.cursor.fetchall():
                print threat_type
                statement = """ SELECT threat_id FROM threat where threat_type='%s'""" % threat_type
                self.cursor.execute(statement)
                subscription_list = []
                query_id_list = []
                for threat_id in self.cursor.fetchall():
                    statement = """SELECT query_id FROM query WHERE threat_id=%s""" % threat_id
                    self.cursor.execute(statement)
                    query_id_list.append(self.cursor.fetchall())
                if not query_id_list:
                    self.qglogger.info("No query is available for %d subscription." % (threat_id) )
                else:
                    subscription_list.append(subscription(threat_id, query_id_list, '2011'))
                    for i in subscription_list:
                        print "threat type subscription packets for %s --> %s" % (threat_id, i.__dict__)
        except Exception, e:
            sys.exit ("Error %s" % (e.args[0]))
            return 0


    def generateSourceThreatTypeSubscriptions(self, source_id=None, threat_id=None):
        print '\n\ngenerateSourceThreatTypeSubscriptionPackets'
        try:
            statement = """SELECT threat_type FROM threat GROUP BY threat_type"""
            self.cursor.execute(statement)
            threat_type_list = self.cursor.fetchall()
            statement = """SELECT source_id FROM source"""
            self.cursor.execute(statement)
            source_id_list = self.cursor.fetchall()
            show = pprint.PrettyPrinter(indent=0)
            for threat_type in threat_type_list:
                print """For threat type = %s""" % threat_type
                statement = """ SELECT threat_id FROM threat where threat_type='%s'""" % threat_type
                self.cursor.execute(statement)
                thread_id_list = self.cursor.fetchall()
                subscription_list = []
                query_id_list = []
                for source_id in source_id_list:
                    #print type(source_id)
                    # This looks for each threat_id which belongs to that threat_type   
                    for threat_id in thread_id_list:
                        #print type(threat_id)
                        statement = """SELECT query_id FROM query WHERE threat_id=%d AND source_id=%d""" % (threat_id[0], source_id[0])
                        #print statement
                        self.cursor.execute(statement)
                        result = self.cursor.fetchall()
                        if result:
                            query_id_list.append(result)
                    if not query_id_list:
                        self.qglogger.info("No query is available for %d subscription." % (threat_type))
                    else:
                        subscription_list.append(subscription(str(source_id) + " " + str(threat_type), query_id_list, '2011'))
                    for s in subscription_list:
                        print "threat type subscription packets --------------->  %s" % (show.pprint(vars(s)))
        except Exception, e:
            sys.exit ("Error %s" % (e.args[0]))
            return 0



    def generateJSONPacketsFromSubscription():
        pass


#--------------------- Additional -------------------------#
def create_query(source_name, source_desc, source_link, threat_type, threat_name, output_type, output, creation_time):
    '''
      Get query information FROM parser and pass to the Query Generator.
    '''
    myquery = query(source_name, source_desc, source_link, threat_type, threat_name, output_type, output, creation_time)
    myquery.insert_query()
    #myquery.print_content()
