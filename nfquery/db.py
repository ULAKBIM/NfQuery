from storm.locals import *
import sys

__all__ = [ 'get_store' ]

__store = None


def get_store(conf=None):
    '''
        Create and return a database connection if not exists yet.
    '''
    global __store
    if conf is None:
        if not __store:
            print 'initiate the db first'
            sys.exit(1)
        else:
            return __store
    else:
        if not __store:
            db = 'mysql://' + conf.db_user  + ':' + conf.db_password + '@' + conf.db_host + '/' + conf.db_name
            database = create_database(db)
            __store = Store(database)
        return __store
