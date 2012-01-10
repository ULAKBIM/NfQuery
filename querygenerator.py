#!/usr/local/bin/python

import simplejson 
import logging
import multiprocessing
import sys
import os.path
import hashlib

# nfquery imports
from query import query
from subscription import subscription
from db import db
from defaults import defaults
from logger import ColoredLogger

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

    def __init__(self, sources):
        multiprocessing.Process.__init__(self)
        self.sources = sources
        logging.setLoggerClass(ColoredLogger)
        self.qglogger = logging.getLogger('QueryGenerator')
        self.qglogger.setLevel(defaults.loglevel)
        self.connection = db.get_database_connection()
        self.cursor = self.connection.cursor()


    def run(self):
        # Check for reconfiguration
        if (defaults.reconfigure_flag):
            self.reconfigureSources()    
        self.checkParsers()
        self.executeParsers()
        #self.subscription = subscription()
        #self.subscription.createSubscriptionTypes()
        #self.generateSubscriptionPackets()


    def reconfigureSources(self):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.qglogger.info('Reconfiguring sources')
        # Delete old sources
        try:
            statement = 'SELECT source_name,parser_id FROM source'
            self.cursor.execute(statement)
            registered_sources = self.cursor.fetchall()
        except Exception, e:
            self.connection.rollback()
            self.qglogger.info('Reconfiguration is not completed')
            self.qglogger.error("Error  %s" % (e.args[0]))
            sys.exit()    

        # If we have something in the database
        if registered_sources is not None:
            # Convert the sources dictionary in configuration file to sources list
            sources_list = []
            for i in range(len(self.sources)):
                sources_list.append(self.sources[i].sourcename)
            # Check if db records exists in source list of configuration file
            for source in registered_sources:
                if not(source[0] in(sources_list)):
                    statement1 = 'DELETE FROM source WHERE source_name="%s"' % source[0]
                    statement2 = 'DELETE FROM parser WHERE parser_id=%d' % source[1]
                    try:
                        self.cursor.execute(statement1)
                        self.cursor.execute(statement2)
                        self.qglogger.info('Source is deleted : %s' % source[0])
                    except Exception, e:
                        self.connection.rollback()
                        self.qglogger.info('Reconfiguration is not completed')
                        self.qglogger.error("Error  %s" % (e.args[0]))
                        sys.exit()
        self.qglogger.info('Reconfiguration is completed')
        sys.exit()
    
        for i in range(len(self.sources)):
            # Calculate the checksum
            conf_checksum = hashlib.md5()   
            # However the parser_name column belongs to the parser table, we'll use it in calculation of the checksum of the source,
            # and the checksum will be stored in source table.
            conf_checksum.update( self.sources[i].sourcename     + 
                                  str(self.sources[i].listtype)  + 
                                  self.sources[i].sourcelink     + 
                                  self.sources[i].sourcefile     +
                                  self.sources[i].parser          +
                                  str(self.sources[i].time_interval)
            )
            statement = 'SELECT source_checksum FROM source WHERE source_name="%s"' % (self.sources[i].sourcename)
            self.cursor.execute(statement)
            dbchecksum = self.cursor.fetchone()
            if not dbchecksum:
                # If can't find a checksum, add this new source
                self.qglogger.info('Adding new source %s' % self.sources[i].sourcename)
                try:
                    statement = 'INSERT INTO parser (parser_script, time_interval) VALUES("%s", %d)' % (self.sources[i].parser, self.sources[i].time_interval)
                    self.cursor.execute(statement)
                    parser_id = self.cursor.lastrowid
                    statement = 'INSERT INTO source (source_name, source_link, list_id, parser_id, source_checksum) VALUES("%s", \'%s\', %d, %d, "%s")' % (
                                self.sources[i].sourcename, self.sources[i].sourcelink, self.sources[i].listtype, parser_id, conf_checksum.hexdigest() )
                    self.cursor.execute(statement)
                    self.qglogger.info('New Source added successfully : "%s"' % self.sources[i].sourcename)
                except Exception, e:
                    self.connection.rollback()
                    self.qglogger.error("Error %s" % e)
                    sys.exit()
            elif str(conf_checksum.hexdigest()) != str(dbchecksum[0]):
                # Update the source information
                self.qglogger.info('Updating the source %s' % self.sources[i].sourcename)
                try:
                    # Update source table
                    statement = 'UPDATE source SET source_link="%s", list_id=%d, source_checksum="%s" WHERE source_name="%s" ' % (
                                self.sources[i].sourcelink, self.sources[i].listtype, conf_checksum.hexdigest(), self.sources[i].sourcename
                                )
                    self.cursor.execute(statement)
                    # Update parser table
                    statement = 'UPDATE parser SET parser_script="%s", time_interval=%d WHERE parser_id=(SELECT parser_id FROM source WHERE source_name="%s")' % (
                                 self.sources[i].parser, self.sources[i].time_interval, self.sources[i].sourcename )
                    self.cursor.execute(statement)
                    self.qglogger.info('Source updated successfully : "%s"' % self.sources[i].sourcename)
                except Exception, e:
                    self.connection.rollback()
                    self.qglogger.error("Error  %s" % (e.args[0]))
                    sys.exit()
            elif str(conf_checksum.hexdigest()) == str(dbchecksum[0]):
                self.qglogger.info('No need to reconfigure source :  %s' % self.sources[i].sourcename)
            else:
                self.qglogger.info('CHECK CODE')
                print 'conf checksum ' + conf_checksum.hexdigest()
                print 'dbchecksum ' + dbchecksum
                sys.exit()
            
        #close the cursor and give the database connection.
        self.cursor.close()
        db.give_database_connection()


    def checkParsers(self):
        '''
            Check if the parser exists in the given path.
        '''
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        for i in range(len(self.sources)):
            if os.path.exists(self.sources[i].parser):
                self.qglogger.info('Parser "%s" Exists, OK!' % self.sources[i].parser)
            else:
                self.qglogger.warning('Parser %s doesn\'t exist\nPlease check the nfquery.conf file' % self.sources[i].parser)

    
    def executeParsers(self):
        self.qglogger.info('In %s' % sys._getframe().f_code.co_name)
        for i in range(len(self.sources)):
            # import parsers
            sys.path.append(defaults.sources_path)
            exec('from ' + (self.sources[i].parser.split('/').pop()).split('.py')[0] + ' import fetch_source, parse_source')
            # call generic parser modules
            # TEMP COMMENT # fetch_source(self.sources[i].sourcelink, self.sources[i].sourcefile)
            parse_source(self.sources[i].sourcename, self.sources[i].sourcefile)


    def generateSubscriptionPackets(self):
        self.qglogger.info('In %s' % sys._getframe().f_code.co_name)
        '''
        '''
        statement = 'SELECT source_id FROM source'
        self.cursor.execute(statement)
        registered_sources = self.cursor.fetchall()
        self.qglogger.info('Generating Subscriptions...')
        for (source_id,) in registered_sources:
            self.generateSourceSubscriptions(source_id)
        self.generateThreatTypeSubscriptions()
        self.generateThreatNameSubscriptions()
        self.generateSourceThreatTypeSubscriptions()
        self.generateSourceThreatNameSubscriptions()
   

    def generateSourceSubscriptions(self, source_id):
        try:
            self.qglogger.info('In %s' % sys._getframe().f_code.co_name)
            statement = """SELECT source_name FROM source WHERE source_id=%d""" % (source_id)
            self.cursor.execute(statement)
            source_name = self.cursor.fetchone()
            subscription_list = []
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
                        subscription_list.append(subscription.getInstance(source_name, query_id_list, '2011'))
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
            sys.exit ("Error %s" % repr(e))
            return 0



    def generateThreatNameSubscriptions(self, threat_id=None):
        self.qglogger.info('In %s' % sys._getframe().f_code.co_name)
        try:
            statement = """SELECT threat_id FROM threat WHERE threat_name<>'NULL' GROUP BY threat_name"""
            self.cursor.execute(statement)
            subscription_list = []
            for threat_id in self.cursor.fetchall():
                statement = """SELECT query_id FROM query WHERE threat_id=%s""" % threat_id
                self.cursor.execute(statement)
                query_id_list = self.cursor.fetchall()
                if not query_id_list:
                    self.qglogger.info("No query is available for %d subscription." % (threat_id) )
                else:
                    subscription_list.append(subscription.getInstance(threat_id, query_id_list, '2011'))
            for i in subscription_list:
                print "threat name subscription packets for %s --> %s" % (threat_id, i.__dict__)
        except Exception, e:
            sys.exit ("Error %s" % repr(e))
            return 0


    def generateThreatTypeSubscriptions(self, threat_type=None):
        self.qglogger.info('In %s' % sys._getframe().f_code.co_name)
        try:
            statement = """SELECT threat_type FROM threat GROUP BY threat_type"""
            self.cursor.execute(statement)
            for threat_type in self.cursor.fetchall():
                print threat_type
                statement = """ SELECT threat_id FROM threat WHERE threat_type='%s'""" % threat_type
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
                    subscription_list.append(subscription.getInstance(threat_id, query_id_list, '2011'))
                    for i in subscription_list:
                        print "threat type subscription packets for %s --> %s" % (threat_id, i.__dict__)
        except Exception, e:
            sys.exit ("Error %s" % repr(e))
            return 0


    def generateSourceThreatTypeSubscriptions(self, source_id=None, threat_id=None):
        self.qglogger.info('In %s' % sys._getframe().f_code.co_name)
        try:
            statement = """SELECT threat_type FROM threat GROUP BY threat_type"""
            self.cursor.execute(statement)
            threat_type_list = self.cursor.fetchall()
            statement = """SELECT source_id FROM source"""
            self.cursor.execute(statement)
            source_id_list = self.cursor.fetchall()
            for threat_type in threat_type_list:
                self.qglogger.debug("Executing For threat type = %s""" % threat_type)
                statement = """ SELECT threat_id FROM threat WHERE threat_type='%s'""" % threat_type
                self.cursor.execute(statement)
                thread_id_list = self.cursor.fetchall()
                subscription_list = []
                query_id_list = []
                for source_id in source_id_list:
                    self.qglogger.debug("Executing For source_id = %d""" % source_id)
                    # This looks for each threat_id which belongs to that threat_type   
                    for threat_id in thread_id_list:
                        statement = """SELECT query_id FROM query WHERE threat_id=%d AND source_id=%d""" % (threat_id[0], source_id[0])
                        self.cursor.execute(statement)
                        result = self.cursor.fetchall()
                        if result:
                            query_id_list.append(result)
                    if not query_id_list:
                        self.qglogger.debug("No query is available for %s subscription." % (threat_type))
                    else:
                        subscription_list.append(subscription.getInstance(str(source_id) + "," + str(threat_type), query_id_list, '2011'))
                    query_id_list = []        
                for s in subscription_list:
                    self.qglogger.debug("threat type subscription packets --------------->  %s" % (s.__dict__))
        except Exception, e:
            sys.exit ("Error %s" % repr(e))
            return 0

    def generateSourceThreatNameSubscriptions(self, source_id=None, threat_id=None):
        self.qglogger.info('In %s' % sys._getframe().f_code.co_name)
        try:
            statement = """SELECT threat_id FROM threat WHERE threat_name IS NOT NULL group by threat_name"""
            self.cursor.execute(statement)
            threat_id_list = self.cursor.fetchall()
            statement = """SELECT source_id FROM source"""
            self.cursor.execute(statement)
            source_id_list = self.cursor.fetchall()
            query_id_list = []
            subscription_list = []
            for source_id in source_id_list:
                self.qglogger.debug("Executing For source_id = %d""" % source_id)
                # This looks for each threat_id which belongs to that threat_type   
                for threat_id in threat_id_list:
                    statement = """SELECT query_id FROM query WHERE threat_id=%d AND source_id=%d""" % (threat_id[0], source_id[0])
                    self.cursor.execute(statement)
                    result = self.cursor.fetchall()
                    if result:
                        query_id_list.append(result)
                        if not query_id_list:
                            self.qglogger.debug("No query is available for %s subscription." % (threat_id))
                        else:
                            subscription_list.append(subscription.getInstance(str(source_id) + "," + str(threat_id), query_id_list, '2011'))
                            query_id_list = []        
            for s in subscription_list:
                self.qglogger.debug("threat type subscription packets --------------->  %s" % (s.__dict__))
                print "threat type subscription packets --------------->  %s" % (s.__dict__)
        except Exception, e:
            sys.exit ("Error %s" % repr(e))
            return 0 


    def generateJSONPacketsFromSubscription():
        pass

# place this function in elsewhere
def create_query(source_name, output_type, output, creation_time):
    '''
      Get query information from parser and insert the query to database.
    '''
    connection = db.get_database_connection()
    cursor = connection.cursor()
    myquery = query(source_name, output_type, output, creation_time)
    myquery.insert_query()
    #myquery.print_content()






