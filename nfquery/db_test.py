# -*- coding: utf8 -*- 
from storm.locals import *
from MySQLdb import Error as MySQLException
from config import Config, ConfigError
import sys
def get_store():
    configfile = "/home/hamza/nfquery/cfg/nfquery.conf"
    try:
        config = Config(configfile)
    except ConfigError, e:
        print "hata olustu"
        sys.exit(1)

    
    db_user = config.database.db_user
    db_host = config.database.db_host
    db_name = config.database.db_name
    db_password = config.database.db_password

    db = 'mysql://' + db_user  + ':' + db_password + '@' + db_host + '/' + db_name
    database = create_database(db)
    store = Store(database)
    return store

