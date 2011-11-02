#!/usr/local/bin/python

import MySQLdb
import time
import sys


__all__ = ['db']


class db:
    '''
        A python singleton class designed for database connection pooling

        db class deals with the db operations. It gets the database configuration parameters
        and initiates database connection instance. The attributes and functions described
        below.

         ----------------
        | Attributes     |
         ----------------

        db_host :

        db_name :

        db_user :

        db_password :

         ----------------
        | Functions      |
         ----------------

        connect_db :

        get_connection_instance:

    '''
    class __db():
        """ Implementation of the singleton interface """
        __connection=None
        def __init__(self, db_host, db_user, db_password, db_name):
             self.db_host = db_host
             self.db_name = db_name
             self.db_user = db_user
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

        def syncConnection(self):
            """
                Commits changes to database
            """
            if self.__connection is None:
                sys.exit('No connection exists, can not sync!\n')
            else:
                self.__connection.commit()

        def closeConnection(self):
            """
                Closes database connection
            """
            if self.__connection is None:
                sys.exit('No connection to close\n Check your code\n')
            else:
                self.__connection.close()


    # storage for the instance reference
    __dbinstance = None
    
    def __init__(self, db_host, db_user, db_password, db_name):
        if db.__dbinstance is None:
            # Create and remember instance
            db.__dbinstance = db.__db(db_host, db_user, db_password, db_name)
            # Store instance reference as the only member in the handle
            self.__dict__['_Singleton__instance'] = db.__dbinstance
            print 'Creating Database Instance\n'
        else:
            print 'Using Existing Database Instance\n'

    @staticmethod
    def get_database_connection():
        '''
            Check whether we already have an instance
            To call this function, dbinstance should already be created with calling the db() class constructor
            with database parameters.
            Otherwise, program exists with error!
        '''
        if db.__dbinstance is None:
            print 'No database instance exists\n Please create a db instance first to get a connection\n'
            sys.exit()
        else:
            return db.__dbinstance.getConnection()

    @staticmethod
    def give_database_connection():
        '''
           Commit changes to database which is done by a temporary connection instance.
           NOT CLOSES THE DB CONNECTION!!
        '''
        db.__dbinstance.syncConnection()

    @staticmethod
    def close_database_connection():
        '''
            Closes the database connection
        '''
        db.__dbinstance.closeConnection()


    #def __getattr__(self, attr):
    #    """ Delegate access to implementation """
    #    return getattr(self.__dbinstance, attr)

    #def __setattr__(self, attr, value):
    #    """ Delegate access to implementation """
    #    return setattr(self.__dbinstance, attr, value)


