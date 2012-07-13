import _mysql
import MySQLdb
from config import Config, ConfigError
import sys

conf_file = "matrice.conf"
create_nodetonode_table="CREATE TABLE IF NOT EXISTS node_to_node (\
                         id int(10) unsigned NOT NULL AUTO_INCREMENT,\
                         fromm varchar(10) CHARACTER SET utf8 COLLATE utf8_turkish_ci NOT NULL,\
                         too varchar(10) CHARACTER SET utf8 COLLATE utf8_turkish_ci NOT NULL,\
                         date date ,\
			 flow varchar(10) CHARACTER SET utf8 COLLATE utf8_turkish_ci NOT NULL,\
			 flow_percent varchar(10) CHARACTER SET utf8 COLLATE utf8_turkish_ci,\
			 byte varchar(10) CHARACTER SET utf8 COLLATE utf8_turkish_ci NOT NULL,\
			 byte_percent varchar(10) CHARACTER SET utf8 COLLATE utf8_turkish_ci,\
			 packet varchar(10) CHARACTER SET utf8 COLLATE utf8_turkish_ci NOT NULL,\
			 packet_percent varchar(10) CHARACTER SET utf8 COLLATE utf8_turkish_ci,\
			 PRIMARY KEY (id)\
			 ) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;"

def parseConfig(conf_file):
    try:
        config = Config(conf_file)
	return config
    except ConfigError, e:
        print("Please check configuration file syntax")
	print("%s" % e)
	sys.exit(1)


def connectdb(config):
    try:
        db=_mysql.connect(config.database.host,config.database.user,config.database.password,config.database.database)
	return db
    except:
        print "can not connect to mysql!"


def createtable(database):
    database.query(create_nodetonode_table)



if __name__ == "__main__":
    config = parseConfig(conf_file)
    db = connectdb(config)
    createtable(db)
    
