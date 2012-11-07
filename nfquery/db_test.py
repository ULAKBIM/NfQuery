from storm.locals import *
from MySQLdb import Error as MySQLException

def returnStore():
    db_user = "root"
    db_host = "localhost"
    db_name = "nfquery"
    db_password = ""

    db = 'mysql://' + db_user  + ':' + db_password + '@' + db_host + '/' + db_name
    database = create_database(db)
    store = Store(database)
    return store
