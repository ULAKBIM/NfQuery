#!/usr/local/bin/python

import simplejson 
import MySQLdb

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
    

__all__ = ['create_query', 'generateSourceSubscriptionPackets']

def create_query(source_name, source_desc, source_link, threat_type, threat_name, output_type, output, creation_time):
    '''
      Get query information from parser and pass to the Query Generator.
    '''
    myquery = query(source_name, source_desc, source_link, threat_type, threat_name, output_type, output, creation_time)
    myquery.insert_query()
    myquery.print_content()

def generateSourceSubscriptionPackets(source_id, cursor1, cursor2):
    try:
        cursor = cursor1
        othercursor  = cursor2
        # Check if such source exist
        cursor.execute("""select source_name from source where source_id=%d""" % (source_id) )
        source_information = cursor.fetchone()
        if not source_information:
            sys.exit("There is no source registered in the database with this name." ) 
        source_name = source_information
        # Check if we have any query for this source
        cursor.execute("""select query_id from query where source_id=%d""" % (source_id) )
        query_id = cursor.fetchall()
        if query_id is None:
            sys.exit("We don't have any query for this source.") 
        else:
            # Generate a list for adding query classes into it.
            query_list = []
            # Fetch all information related with this source and generate query packet.
            for qid in query_id:
                # Fetch query information
                statement = ("""SELECT subscription_query.query_id FROM subscription,subscription_query WHERE subscription.subscription_desc='%s' AND subscription.subscription_id=subscription_query.subscription_id""" % (source_name))
                othercursor.execute(statement)
                query_id_list = othercursor.fetchall()
                if query_id_list:
                    subscription_list = []
                    for (query_id,) in query_id_list:
                        othercursor.execute(""" select ip.ip from query,query_ip,ip where query.query_id=%s and query.query_id=query_ip.query_id and query_ip.ip_id=ip.ip_id""", (query_id))
                        ip_list = othercursor.fetchall()
                        # subscription_desc, subs
                        # Generate the subscription object
                        subscription_list.append(subscription(source_name, query_id_list, '2011'))
    except Exception, e:
        print 'NOT!'
        import sys
        sys.exit ("Error %s" % (e.args[0]))
        return 0
    
    return subscription_list        

    

def generateThreatSubscription(source_id, threat_id):
    pass

def generateJSONPacketsFromSubscription():
    pass


