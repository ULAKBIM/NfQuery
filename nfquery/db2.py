#!/usr/local/bin/python


from storm.locals import *
from logger import createLogger

class db2:

    def __init__(self, db_host, db_user, db_password, db_name):
        self.db_host = db_host
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.qrlogger = createLogger('QueryRepository')
        self.store = None
            

    def get_store(self):
        if not self.store:
            db = 'mysql://' + self.db_user  + ':' + self.db_password + '@' + self.db_host + '/' + self.db_name
            #print db
            database = create_database(db)
            self.store = Store(database)
        return self.store
