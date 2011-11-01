#!/usr/local/bin/python 

import MySQLdb
import time
import sys



class SingletonDatabase:
    """ A python singleton """

    class __db():
        """ Implementation of the singleton interface """
        __connection=None
        def __init__(self, db_host, db_user, db_password, db_name):
             self.db_host = db_host
             self.db_name = db_name
             self.db_user = db_user
             # We should do something for storing the password, It should be encrypted or hashed?
             self.db_password = db_password

        def getID(self):
            """ Test method, return singleton id """
            return id(self)

        def getConnection(self):
            """ Test method, return connection """
            if self.__connection is None:
                '''                                                                                                             
                   Establishes mysql connection.
                '''
                try :
                   self.__connection = MySQLdb.connect(self.db_host, self.db_user, self.db_password, self.db_name)
                   print 'Database Connection Established'
                   return self.__connection
                except MySQLdb.Error, e:
                   sys.exit ("Error %d: %s" % (e.args[0], e.args[1]))
            else:
                print 'Existing Database Connection Returned\n'
                return self.__connection
    

    # storage for the instance reference
    __dbinstance = None
    
    def __init__(self, db_host, db_user, db_password, db_name):
        if SingletonDatabase.__dbinstance is None:
            # Create and remember instance
            SingletonDatabase.__dbinstance = SingletonDatabase.__db(db_host, db_user, db_password, db_name)
            print 'Creating SingletonDatabase Class\n'
        else:
            print 'Using Existing SingletonDatabase Class\n'

    @staticmethod
    def getDatabaseConnection():
        """ Create singleton instance """
        # Check whether we already have an instance
        if SingletonDatabase.__dbinstance is None:
            # Create and remember instance
            #SingletonDatabase.__dbinstance = SingletonDatabase.__db(db_host, db_user, db_password, db_name)
            print 'No instance exists\n'
            sys.exit()
        else:
            print 'Returns existing connection\n'
            return SingletonDatabase.__dbinstance.getConnection()
            

        # Store instance reference as the only member in the handle
        self.__dict__['_Singleton__instance'] = SingletonDatabase.__dbinstance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__dbinstance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__dbinstance, attr, value)


if __name__ == "__main__":
    s1 = SingletonDatabase('localhost','nfquery','nf1!','nfquery')
    print "s1=%d, classid=%d, connectionID=%d" % (id(s1), s1.getID(), id(s1.getDatabaseConnection()))
    print "s2 ConnectionID=%s" %  str(id(SingletonDatabase.getDatabaseConnection()))
    print "s3 ConnectionID=%s" %  str(id(SingletonDatabase.getDatabaseConnection()))
    print "s4 ConnectionID=%s" %  str(id(SingletonDatabase.getDatabaseConnection()))

