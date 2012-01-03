#!/usr/local/bin/python

from db import db
import logging
import sys

class subscription():
    
    def __init__(self):
        connection = db.get_database_connection()
        self.cursor = connection.cursor()
        self.initiateLogger('Subscription')
        self.logger.info('In %s' % sys._getframe().f_code.co_name)
        self.logger.info('Initializing new subscription(with default)')

    @classmethod
    def getInstance(self, subscription_name, subscription_query_list, subscription_update_time):
        print 'In %s' % sys._getframe().f_code.co_name 
        print 'Initializing new subscription(with instance)'
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
        subscription_type=1
        statement = '''SELECT source_name FROM source GROUP BY source_name'''
        self.cursor.execute(statement)
        source_name_list = self.cursor.fetchall()
        for subscription_desc in source_name_list:
            statement = '''INSERT IGNORE INTO subscription(subscription_type,subscription_desc) VALUES(%d,'%s')''' % (subscription_type, subscription_desc[0])
            try:
                self.cursor.execute(statement)
                print '\033[1;36m ' + statement + ' \033[1;m'
            except Exception, e:
                sys.exit ("Error %s" % (repr(e)))
                return 0

        self.logger.info('"source" subscription types generated\n')

        # 2) source name + threat_type
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
                #self.cursor.fetchall()[0]
                subscription_desc = str(self.cursor.fetchone()[0]) + "," + str(threat_type[0])
                statement = '''INSERT IGNORE INTO subscription(subscription_type,subscription_desc) VALUES('%s','%s')''' % (subscription_type,subscription_desc)
                try:
                    self.cursor.execute(statement)
                    print '\033[1;36m ' + statement + ' \033[1;m'
                except Exception, e:
                    sys.exit ("Error %s" % (repr(e)))
                    return 0

        self.logger.info('"source + threat_type" subscription types generated\n')
        
        # 3) source_name + threat_type + threat_name
        subscription_type=3
        for source_id in source_id_list:
            statement = '''SELECT threat_id FROM source_threat_relation WHERE source_id=%d AND threat_id IN(SELECT threat_id FROM threat WHERE threat_name IS NOT NULL)''' % (source_id)
            self.cursor.execute(statement)
            threat_id_list = self.cursor.fetchall()
            for threat_id in threat_id_list:
                statement = ''' SELECT threat_type, threat_name FROM threat WHERE threat_id=%d''' % (threat_id)
                self.cursor.execute(statement)
                threat_type, threat_name = self.cursor.fetchone()
                statement = '''SELECT source_name FROM source where source_id=%d''' % source_id[0]                
                self.cursor.execute(statement)
                source_name = self.cursor.fetchone()
                subscription_desc = str(source_name[0]) + ',' + str(threat_type) + ',' + str(threat_name)
                statement = '''INSERT IGNORE INTO subscription(subscription_type,subscription_desc) VALUES('%s', '%s')''' % (subscription_type, subscription_desc)
                try:
                    self.cursor.execute(statement)
                    print '\033[1;36m ' + statement + ' \033[1;m'
                except Exception, e:
                    sys.exit ("Error %s" % (repr(e)))
                    return 0

        self.logger.info('\033[1;33m"source + threat_type + threat_name" subscription types generated\033[1;m\n')

        # 4) threat type
        subscription_type=4
        statement = '''SELECT threat_type FROM threat GROUP BY threat_type'''
        self.cursor.execute(statement)
        threat_type_list = self.cursor.fetchall()
        for threat_type in threat_type_list:
            statement = '''INSERT IGNORE INTO subscription(subscription_type,subscription_desc) VALUES('%s', '%s')''' % (subscription_type,threat_type[0])
            try:
                self.cursor.execute(statement)
                print '\033[1;36m ' + statement + ' \033[1;m'
            except Exception, e:
                sys.exit ("Error %s" % (repr(e)))
                return 0
            
        self.logger.info('\033[1;33m"threat_type" subscription types generated\033[1;m\n')

        # 5) threat name 
        subscription_type=5
        statement = '''SELECT threat_name FROM threat WHERE threat_name IS NOT NULL'''
        self.cursor.execute(statement)
        threat_name_list = self.cursor.fetchall() 
        for threat_name in threat_name_list:
            statement = '''INSERT IGNORE INTO subscription(subscription_type,subscription_desc) VALUES('%s', '%s')''' % (subscription_type,threat_name[0])
            try:
                self.cursor.execute(statement)
                print '\033[1;36m ' + statement + ' \033[1;m'
            except Exception, e:
                sys.exit ("Error %s" % (repr(e)))
                return 0

        self.logger.info('\033[1;33m"threat_name" subscription types generated\033[1;m\n')

        #close the cursor and give the database connection.
        self.cursor.close()
        db.give_database_connection()

