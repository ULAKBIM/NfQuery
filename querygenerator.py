#!/usr/local/bin/python

import simplejson 
import logging
import multiprocessing
import sys
import os.path
import hashlib
import MySQLdb

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
            sys.exit()

        self.checkParsers()
        self.executeParsers()
        self.subscription = subscription()
        #self.subscription.createSubscriptionTypes()
        self.generateSubscriptionPackets()


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
        
        #self.reconfigureSubscriptions() # ?????
            
        #close the cursor and give the database connection.
        self.cursor.close()
        db.sync_database_connection()


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
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        for i in range(len(self.sources)):
            # import parsers
            sys.path.append(defaults.sources_path)
            exec('from ' + (self.sources[i].parser.split('/').pop()).split('.py')[0] + ' import fetch_source, parse_source')
            # call generic parser modules
            # TEMP COMMENT # fetch_source(self.sources[i].sourcelink, self.sources[i].sourcefile)
            parse_source(self.sources[i].sourcename, self.sources[i].sourcefile)


    def generateSubscriptionPackets(self):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.qglogger.info('Generating Subscriptions...')
        self.generateSourceSubscriptions()
        self.generateListTypeSubscriptions()
   

    def generateSourceSubscriptions(self):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        try:
            # Check if source_name is not given, so we work for all sources.
            statement = """SELECT subscription_name FROM subscription WHERE subscription_type=1"""
            self.cursor.execute(statement)
            source_name_list = self.cursor.fetchall()
            if source_name_list is None:
                self.qglogger.error("Source is not registered to database. Run reconfig or check sources.")
                sys.exit()
            self.qglogger.debug(source_name_list)
            for source_name in source_name_list:
                statement = """SELECT query_id FROM query WHERE source_id IN(SELECT source_id FROM source WHERE source_name='%s')""" % source_name[0]
                self.cursor.execute(statement)
                query_id_list = self.cursor.fetchall()
                if query_id_list is None:
                    self.qglogger.debug("We don't have any query for this source.")
                    self.qglogger.error("%s subscription creation is failed." % (source_name) )   # We exit, but may be we can wait for the parser to be executed.
                    sys.exit()
                statement = """SELECT subscription_id FROM subscription WHERE subscription_name='%s'""" % source_name
                self.cursor.execute(statement)
                subscription_id = self.cursor.fetchone()
                statement = """SELECT subs_query_id FROM subscription_query WHERE subscription_id=%d""" % subscription_id
                self.cursor.execute(statement)
                subs_query_id = self.cursor.fetchone()
                if subs_query_id is None:
                    for qid in query_id_list:
                        ########### eger subs_query_id varsa burada update yapilacak, yoksa eklenecek 
                        statement = ( """INSERT INTO subscription_query(subscription_id, query_id)""" + 
                                      """VALUES(%d, %d)""" % (subscription_id[0], qid[0]) )
                        self.cursor.execute(statement)
                        self.qglogger.debug(statement)
                else:
                    statement = ("""SELECT query_id FROM subscription_query WHERE subscription_id=%d""" % subscription_id[0])
                    self.cursor.execute(statement)
                    query_ids = self.cursor.fetchall()
                    for qid in query_id_list:
                        if not (qid in query_ids):
                            statement = ( """INSERT INTO subscription_query(subscription_id, query_id)""" +
                                      """VALUES(%d, %d)""" % (subscription_id[0], qid[0]) )
                            self.cursor.execute(statement)
                            self.qglogger.debug(statement)
        except MySQLdb.IntegrityError, message:
            errorcode = message[0] # get MySQL error code
            if errorcode == 1062:
                self.qglogger.debug('Duplicate Entry Warning / No Problem.')
                self.qglogger.info('Duplicate Entry Warning / No Problem.')
            else:
                self.qglogger.error("'Error %s" % (repr(e)))
                sys.exit()
        except Exception, e:
            self.qglogger.error("Error %s" % (repr(e)))
            sys.exit ()
            return 0
        db.sync_database_connection()



    def generateListTypeSubscriptions(self):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        try:
            # Check if source_name is not given, so we work for all sources.
            statement = """SELECT subscription_name FROM subscription WHERE subscription_type=2"""
            self.cursor.execute(statement)
            list_type_list = self.cursor.fetchall()
            if list_type_list is None:
                self.qglogger.error("List type is not registered to database. Run reconfig or check sources.")
                sys.exit()
            self.qglogger.debug(list_type_list)
            for list_type in list_type_list:
                statement = """SELECT query_id FROM query WHERE source_id IN (SELECT source_id FROM source where list_id IN(SELECT list_id FROM list WHERE list_type='%s'))""" % list_type[0]
                self.cursor.execute(statement)
                query_id_list = self.cursor.fetchall()
                if query_id_list is None:
                    self.qglogger.debug("We don't have any query for this list type.")
                    self.qglogger.error("%s subscription is failed." % (list_type[0]) ) 
                else:
                    statement = """SELECT subscription_id FROM subscription WHERE subscription_name='%s'""" % list_type[0]
                    self.cursor.execute(statement)
                    subscription_id = self.cursor.fetchone()
                    statement = """SELECT subs_query_id FROM subscription_query WHERE subscription_id=%d""" % subscription_id
                    self.cursor.execute(statement)
                    subs_query_id = self.cursor.fetchone()
                if subs_query_id is None:
                    for qid in query_id_list:
                        ########### eger subs_query_id varsa burada update yapilacak, yoksa eklenecek 
                        statement = ( """INSERT INTO subscription_query(subscription_id, query_id)""" +
                                      """VALUES(%d, %d)""" % (subscription_id[0], qid[0]) )
                        self.cursor.execute(statement)
                        self.qglogger.debug(statement)
                else:
                    statement = ("""SELECT query_id FROM subscription_query WHERE subscription_id=%d""" % subscription_id[0])
                    self.cursor.execute(statement)
                    query_ids = self.cursor.fetchall()
                    for qid in query_id_list:
                        if not (qid in query_ids):
                            statement = ( """INSERT INTO subscription_query(subscription_id, query_id)""" +
                                      """VALUES(%d, %d)""" % (subscription_id[0], qid[0]) )
                            self.cursor.execute(statement)
                            self.qglogger.debug(statement)
        except MySQLdb.IntegrityError, message:
            errorcode = message[0] # get MySQL error code
            if errorcode == 1062:
                self.qglogger.debug('Duplicate Entry Warning / No Problem.')
                self.qglogger.info('Duplicate Entry Warning / No Problem.')
            else:
                self.qglogger.error("'Error %s" % (repr(e)))
                sys.exit()
        except Exception, e:
            self.qglogger.error("Error %s" % (repr(e)))
            sys.exit ()
            return 0
        db.sync_database_connection()


    def generateJSONPacketsFromSubscription():
        pass



# place this function in elsewhere
def create_query(source_name, output_type, output, creation_time):
    '''
      Get query information from parser and insert the query to database.
    '''
    myquery = query(source_name, output_type, output, creation_time)
    myquery.insert_query()
    #myquery.print_content()






