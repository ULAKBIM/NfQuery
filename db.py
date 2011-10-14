#!/usr/local/bin/python

import MySQLdb


__all__ = ['db']


class db():
    '''
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

    def __init__(self, db_host, db_user, db_password, db_name):
        self.db_host = db_host
        self.db_name = db_name
        self.db_user = db_user
        # We should do something for storing the password, It should be encrypted or hashed?
        self.db_password = db_password
        self.connection = self.connect_database()

    def connect_database(self):
        '''
           Establishes mysql connection.
        '''
        try :
           connection = MySQLdb.connect(self.db_host, self.db_user, self.db_password, self.db_name)
           print 'Database connection established'
           return connection
        except MySQLdb.Error, e:
           sys.exit ("Error %d: %s" % (e.args[0], e.args[1]))

    def get_connection(self):
        if self.connection:
            return self.connection
        else:
            print 'No database connection exists'

    def end_connection(self):
        '''
           Commit changes to database and close the connection.
        '''
        self.connection.commit()
        self.connection.close()
        print 'Database connection closed'
