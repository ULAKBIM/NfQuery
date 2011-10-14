#!/usr/local/bin/python

import simplejson 
import MySQLdb
import logging
import multiprocessing
import sys

# nfquery imports
from query import query
from subscription import subscription

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
    
    def __init__(self, cursor, parsers):
        multiprocessing.Process.__init__(self)
        self.cursor = cursor
        self.parsers = parsers

    def run(self):
        print 'In %s' % self.name
        self.executeParsers()
        self.generateSubscriptionPackets()
        # Routines
        # prepare subscriptions according to existing categories.
        pass

    def executeParsers(self):
        if not self.parsers:
            sys.exit('No parser is found, please check your nfquery.conf file!')
        else:
            parser_list = self.parsers.split(',')
        if(checkParsers(parser_list)):
            print 'Parsers are OK, Lets start executing each parser.'
        else:
            sys.exit('You do something wrong with the parser names.')
            



    def checkParsers(self, parser_list):
        # fetch registered parser names from the database and check them with existing parser file names.
        statement = 'select parser_desc from parser'
        cursor.execute(statement)
        registered_parsers = cursor.fetchall()
        parsers = ()
        
        # Convert 'tuple of tuples' to 'a single tuple'
        for (p,) in registered_parsers:
            parsers = parsers + (p,)
        
        # Check for each parser, if it is registered.
        for parser in parser_list:
            if parser in parsers:
                print 'Parser Exists, OK!'
            else:
                return 0
                #sys.exit('Parser doesn\'t exist, NOT!')
        return 1        


    def generateSubscriptionPackets(self):
        '''
           Starts the parsers, generates queries and passes to query manager for releasing.
        '''
        print 'aaaa'
        self.generateSourceSubscriptionPackets(1, self.cursor)
        print 'Generating source subscriptions'
        pass
    
    def generateSourceSubscriptionPackets(self, source_id, cursor1):
        '''
            # Check if such source exist
            # Check if we have any query for this source
            # Generate a list for adding query classes into it.
            # Fetch all information related with this source and generate query packet.
            # Fetch query information
        '''
        cursor = cursor1
        try:
            statement = """select source_name from source where source_id=%d""" % (source_id)
            cursor.execute(statement)
            source_information = cursor.fetchone()
            if not source_information:
                sys.exit("There is no source registered in the database with this name.") 
            source_name = source_information
            statement = """select query_id from query where source_id=%d""" % (source_id)
            cursor.execute(statement)
            query_id = cursor.fetchall()
            if query_id is None:
                sys.exit("We don't have any query for this source.") 
            else:
                query_list = []
                for qid in query_id:
                    statement = (                                                                                                                                                                                                    """SELECT subscription_query.query_id FROM subscription,subscription_query                                                                                                                             WHERE subscription.subscription_desc='%s'                                                                                                                                                           AND subscription.subscription_id=subscription_query.subscription_id                                                                                                                              """                                                                                                                                                                                                 % (source_name)                                                                                                                                                                                    )
                    cursor.execute(statement)
                    query_id_list = cursor.fetchall()
                    if query_id_list:
                        subscription_list = []
                        subscription_list.append(subscription(source_name, query_id_list, '2011'))
                        ###### gather subscription information #####   
                        #for (query_id,) in query_id_list:
                        #    cursor.execute(""" select ip.ip from query,query_ip,ip where query.query_id=%s and query.query_id=query_ip.query_id and query_ip.ip_id=ip.ip_id""", (query_id))
                        #    ip_list = cursor.fetchall()
                        #    # subscription_desc, subs
                        #    # Generate the subscription object
                        ############################################
        except Exception, e:
            sys.exit ("Error %s" % (e.args[0]))
            return 0

        for i in subscription_list:
            print i.__dict__
        return subscription_list        
    
    
    def generateThreatSubscription(source_id, threat_id):
        pass
    
    def generateJSONPacketsFromSubscription():
        pass


#--------------------- Additional -------------------------#
def create_query(source_name, source_desc, source_link, threat_type, threat_name, output_type, output, creation_time):
    '''
      Get query information from parser and pass to the Query Generator.
    '''
    myquery = query(source_name, source_desc, source_link, threat_type, threat_name, output_type, output, creation_time)
    myquery.insert_query()
    myquery.print_content()
