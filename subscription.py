#!/usr/local/bin/python


from db import db
from logger import ColoredLogger
from defaults import defaults

import logging
import sys
import MySQLdb

class subscription():
    
    def __init__(self):
        connection = db.get_database_connection()
        self.cursor = connection.cursor()
        self.initiateLogger('SubscriptionGenerator')
        self.slogger.debug('In %s' % sys._getframe().f_code.co_name)

    #@classmethod
    #def getInstance(self, subscription_name, subscription_query_list, subscription_update_time):
    #    print 'In %s' % sys._getframe().f_code.co_name 
    #    print 'Initializing new subscription(with instance)'
    #    self.subscription_name = subscription_name
    #    self.subscription_query_list = subscription_query_list
    #    self.subscription_update_time = subscription_update_time
    #    return self

    def initiateLogger(self, logger_name):
        logging.setLoggerClass(ColoredLogger)
        self.slogger = logging.getLogger('SubscriptionGenerator')
        self.slogger.setLevel(defaults.loglevel)
        self.slogger.debug('In %s' % sys._getframe().f_code.co_name)

    def createSubscriptionTypes(self):
        self.slogger.debug('In %s' % sys._getframe().f_code.co_name)
        '''
            We have 2 different subscription types.
            
            1) Source -> example : "Amada,Malc0de,DFN-Honeypot,ABC-NREN_Special_Source"
            2) List Type -> example : "Botnet,Malware,Honeypot Output, Special Source Output"
            
            These subscription types are inserted into subscription table
            according to the condition of "if that subscription type have queries" 
            in query table. "createSubscriptions" function fills the subscription 
            table by inserting these subscription types. 


			!!!!!! SUBSCRIPTION_TAGS NE OLACAK !!!!!!!!


        '''

        # 1) source name
        subscription_type=1
        statement = '''SELECT source_name FROM source GROUP BY source_name'''
        self.cursor.execute(statement)
        source_name_list = self.cursor.fetchall()
        for subscription_name in source_name_list:
            statement = '''INSERT INTO subscription(subscription_type, subscription_name) VALUES(%d,'%s')''' % (subscription_type, subscription_name[0])
            try:
                self.cursor.execute(statement)
                print statement
            except MySQLdb.IntegrityError, message:
                errorcode = message[0] # get MySQL error code
                if errorcode == 1062:
                    self.slogger.debug('Duplicate Entry Warning / No Problem.')
            except Exception, e:
                sys.exit ("Error %s" % (repr(e)))
                return 0

        self.slogger.info('"source" subscription types generated')

        # 2) List Type
        subscription_type=2
        statement = '''SELECT list_type FROM list GROUP BY list_type'''
        self.cursor.execute(statement)
        list_type_list = self.cursor.fetchall()
        for list_type in list_type_list:
            statement = '''INSERT INTO subscription(subscription_type, subscription_name) VALUES('%s', '%s')''' % (subscription_type, list_type[0])
            try:
                self.cursor.execute(statement)
                print statement 
            except MySQLdb.IntegrityError, message:
                errorcode = message[0] # get MySQL error code
                if errorcode == 1062:
                    self.slogger.debug('Duplicate Entry Warning / No Problem.')
            except Exception, e:
                sys.exit ("Error %s" % (repr(e)))
                return 0
        self.slogger.info('list_type subscriptions generated')

        #close the cursor and give the database connection.
        self.cursor.close()
        db.sync_database_connection()

