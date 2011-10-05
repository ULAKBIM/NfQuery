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
        self.connect_database()

    def connect_database(self):
        '''
           Establishes mysql connection.
        '''
        try :
           self.connection = MySQLdb.connect(self.db_host, self.db_user, self.db_password, self.db_name)
        except MySQLdb.Error, e:
           #print "Error %d: %s" % (e.args[0], e.args[1])
           sys.exit ("Error %d: %s" % (e.args[0], e.args[1]))

    def get_database_cursor(self):
        if not self.connection:
            connect_database()
        else:
           self.cursor = self.connection.cursor()
        return self.cursor  
    
    def end_database_cursor(self):
        if not self.cursor:
            print 'cursor is already closed\n'
        else:
            self.cursor.close()
            # we can divide here and may be not close the database connection
            self.close_database()
 
    def close_database(self):
        '''
           Commit changes to database and close the connection.
        '''
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
