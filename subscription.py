#!/usr/local/bin/python

from db import db
from ansistrm import ColorizingStreamHandler
import logging
import sys

class subscription():
    
    def __init__(self):
        connection = db.get_database_connection()
        self.cursor = connection.cursor()
        self.initiateLogger('Subscription')
        self.logger.info('In %s' % sys._getframe().f_code.co_name)
        self.logger.info('Initializing new subscription with constructor')

    @classmethod
    def getInstance(self, subscription_name, subscription_query_list, subscription_update_time):
        print 'In %s' % sys._getframe().f_code.co_name 
        print 'Initializing new subscription instance'
        self.subscription_name = subscription_name
        self.subscription_query_list = subscription_query_list
        self.subscription_update_time = subscription_update_time
        return self

    def initiateLogger(self, logger_name):
        self.logger = logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(logger_name)
        self.logger.info('In %s' % sys._getframe().f_code.co_name)

    def createSubscriptionTypes(self):
        self.logger.info('In %s' % sys._getframe().f_code.co_name)
        '''
            We have 4 different subscription types.
            
            1) Source -> example : "Amada"
            2) Source + Threat Type -> example : "Amada,Botnet"
            3) Source + Threat Type + Threat Name -> example : "Amada,Botnet,Spyeye"
            4) Threat Type -> example : "Botnet"
            5) Threat Name -> example : "Spyeye"
            
            These subscription types are inserted into subscription table
            according to the condition of "if that subscription type have queries" 
            in query table.  Subscription types are consist of the permutation of 
            source_name, threat_type and threat_name fields in the database tables 
            "threat" and "source". So createSubscriptions function fills the subscription 
            table by inserting these subscription types. It should be run in a time 
            period for the new subscription types to be added to the subscription table. 
        '''

        # 1) source name
        # SELECT source_name from source group by source_name;
        subscription_type=1
        statement = '''SELECT source_name FROM source GROUP BY source_name'''
        self.cursor.execute(statement)
        source_name_list = self.cursor.fetchall()
        for subscription_desc in source_name_list:
            statement = '''INSERT INTO subscription(subscription_type,subscription_desc) VALUES('%s','%s')''' % (subscription_type, subscription_desc)
            #cursor.execute(statement)
            print statement

        self.logger.info('"source" subscription types generated\n')

        # 2) source name + threat_type
        # SELECT source_id from query group by source_id;
        # fetchall
        # for i in fetchall
        #    SELECT threat_type from threat where threat_id IN(SELECT threat_id from query where source_id=i group by threat_id);
        #    fetchall
        #    for j in fetchall
        #       source_name,threat_type

        subscription_type=2
        statement = '''SELECT source_id FROM source GROUP BY source_id'''
        self.cursor.execute(statement)
        source_id_list = self.cursor.fetchall()
        for source_id in source_id_list:
            statement = '''SELECT threat_type FROM threat group by threat_type'''
            self.cursor.execute(statement)
            threat_type_list = self.cursor.fetchall()
            for threat_type in threat_type_list:
                statement = '''SELECT source_name FROM source where source_id=%d''' % (source_id)
                self.cursor.execute(statement)
                subscription_desc = str(self.cursor.fetchone()) + "," + str(threat_type)
                statement = '''INSERT INTO subscription(subscription_type,subscription_desc) VALUES('%s','%s')''' % (subscription_type,subscription_desc)
                #cursor.execute(statement)
                print statement

        self.logger.info('"source + threat_type" subscription types generated\n')
        
        # 3) source_name + threat_type + threat_name
        # 
        # fetchall
        # for i in fetchall
        #    SELECT threat_type from threat where threat_id IN(SELECT threat_id from query where source_id=i group by threat_id) group by threat_type;
        #    fetchall
        #    for j in fetchall
        #       SELECT threat_name from threat where threat_type=j
        #       source_name,threat_type,threat_name

        subscription_type=2

        
        
        
        self.logger.info('"source + threat_type + threat_name" subscription types generated')

        #subscription_type=3
        #for source_name in source_name_list:


             

        
        # 4) threat type
        # SELECT threat_type from threat where threat_id IN(SELECT threat_id from query group by threat_id) group by threat_type;

        # 5) threat name 
        # SELECT threat_name from threat where threat_id IN(SELECT threat_id from query group by threat_id) and threat_name is not null  group by threat_name ;


    def generateJSONPacketsFromSubscription(self):
        pass






