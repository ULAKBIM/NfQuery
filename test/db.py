#!/usr/local/bin/python 

import MySQLdb
import time

class Singleton:
    """ A python singleton """

    class __database:
        """ Implementation of the singleton interface """

        __connection = None

        def __init__(self, db_host, db_user, db_password, db_name):
            self.db_host = db_host
            self.db_name = db_name
            self.db_user = db_user
            # We should do something for storing the password, It should be encrypted or hashed?
            self.db_password = db_password 
            self.connect_database()
            self.testDB()

        def connect_database(self):
            '''
               Establishes mysql connection.
            '''
            try :
               self.__connection = MySQLdb.connect(self.db_host, self.db_user, self.db_password, self.db_name)
               print 'Database connection established'
               return self.__connection
            except MySQLdb.Error, e:
               sys.exit ("Error %d: %s" % (e.args[0], e.args[1]))

    
        def testDB(self):
            cursor = self.__connection.cursor()
            while True:
                cursor.execute('select 1')
                result = cursor.fetchall()
                print result
                time.sleep(3)


        def get_id(self):
            """ Test method, return singleton id """
            return id(self)

        def get_connection_id(self):
            """ Test method, return singleton id """
            return id(self.__connection)


    # storage for the instance reference
    __instance = None

    #def __init__(self, ):
    #    """ Create singleton instance """
    #    # Check whether we already have an instance
    #    if Singleton.__instance is None:
    #        # Create and remember instance
    #        Singleton.__instance = Singleton.__impl()

    def __init__(self, db_host, db_user, db_password, db_name):
        """ Create singleton instance """
        if Singleton.__instance is None:
            # Create and remember instance
            Singleton.__instance = Singleton.__database(db_host, db_user, db_password, db_name)

        # Store instance reference as the only member in the handle
        self.__dict__['_Singleton__instance'] = Singleton.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)


def get():
    print id(Singleton.__instance)


if __name__ == "__main__":
    s1 = Singleton('localhost','nfquery','nf1!','nfquery')
    print id(s1), s1.get_id(), s1.get_connection_id()
    #
    #s2 = Singleton('localhost','nfquery','nf1!','nfquery')
    #print id(s2), s2.get_id(), s2.get_connection_id()

# Sample output, the second (inner) id is constant:
# 8172684 8176268
# 8168588 8176268

