from storm.locals import *
from MySQLdb import Error as MySQLException
import sys


__all__ = [ 'get_store' ]

__store = None

def initialize_db(store):

    store.execute(
                  "CREATE TABLE prefix("                                             + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "prefix VARCHAR(100) COLLATE utf8_unicode_ci NOT NULL,"            +
                  "PRIMARY KEY (id)"                                                 +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"      
                 )
   
    store.execute(
                  "CREATE TABLE plugin("                                             + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "organization VARCHAR(30) COLLATE utf8_unicode_ci NOT NULL,"       +
                  "adm_name VARCHAR(30) COLLATE utf8_unicode_ci NOT NULL,"           +
                  "adm_mail VARCHAR(30) COLLATE utf8_unicode_ci NOT NULL,"           +
                  "adm_tel VARCHAR(20) COLLATE utf8_unicode_ci NOT NULL,"            +
                  "adm_publickey_file VARCHAR(50) COLLATE utf8_unicode_ci NOT NULL," +
                  "prefix_id INT UNSIGNED NOT NULL,"                                 +
                  "plugin_ip VARCHAR(20) COLLATE utf8_unicode_ci NOT NULL,"          +
                  "checksum VARCHAR(32) COLLATE utf8_unicode_ci NOT NULL,"           +
                  "registered TINYINT NOT NULL,"                                     +
                  "PRIMARY KEY (id),"                                                +
                  "UNIQUE KEY plugin_ip (plugin_ip),"                                +
                  "FOREIGN KEY (prefix_id) REFERENCES prefix(id)"                    +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )


    store.execute(
                  "CREATE TABLE parser("                                             + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "name VARCHAR(75) COLLATE utf8_unicode_ci NOT NULL,"               +
                  "time_interval SMALLINT(6) NOT NULL,"                              +
                  "PRIMARY KEY (id)"                                                +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )


    store.execute(
                  "CREATE TABLE threat("                                             + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "type VARCHAR(20) COLLATE utf8_unicode_ci NOT NULL,"               +
                  "UNIQUE KEY type (type),"                                          + 
                  "PRIMARY KEY (id)"                                                +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE source("                                             +
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "name VARCHAR(75) COLLATE utf8_unicode_ci NOT NULL,"               +
                  "parser_id INT UNSIGNED NOT NULL,"                                 +
                  "checksum VARCHAR(32) COLLATE utf8_unicode_ci NOT NULL,"           +
                  "link VARCHAR(75) COLLATE utf8_unicode_ci NOT NULL,"               +
                  "threat_id int unsigned NOT NULL,"                                 +
                  "FOREIGN KEY (threat_id) REFERENCES threat (id),"                  +
                  "FOREIGN KEY (parser_id) REFERENCES parser (id) ON UPDATE CASCADE,"+
                  "PRIMARY KEY (id)"                                                +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE query ("                                             + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         + 
                  "source_id INT UNSIGNED NOT NULL,"                                 +
                  "update_time VARCHAR(20),"                                         + 
                  "type SMALLINT UNSIGNED NOT NULL,"                                 + 
                  "checksum VARCHAR(32) NOT NULL,"                                   + 
                  "creation_time VARCHAR(20) NOT NULL,"                              + 
                  "PRIMARY KEY (id),"                                                +
                  "FOREIGN KEY (source_id) REFERENCES source(id) ON DELETE CASCADE" + 
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE subscription("                                       + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "type SMALLINT unsigned NOT NULL,"                                 +
                  "name VARCHAR(50) COLLATE utf8_unicode_ci NOT NULL,"               +
                  "PRIMARY KEY (id),"                                                +
                  "UNIQUE KEY name (name)"                                           +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE subscription_packet("                                + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "subscription_id INT UNSIGNED NOT NULL,"                           +
                  "query_id INT UNSIGNED NOT NULL,"                                  +
                  "tags VARCHAR(50) COLLATE utf8_unicode_ci NOT NULL DEFAULT 'NULL'," + 
                  "PRIMARY KEY (id),"                                                +
                  "FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE,"   +
                  "FOREIGN KEY (subscription_id) REFERENCES subscription(id) ON DELETE CASCADE" +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE ip("                                                 +
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "ip VARCHAR(20) COLLATE utf8_unicode_ci NOT NULL,"                 +
                  "ip_int BIGINT(20) UNSIGNED NOT NULL,"                             +
                  "PRIMARY KEY (id)"                                                 +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE src_ip("                                             + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "query_id INT UNSIGNED NOT NULL,"                                  +
                  "ip_id INT UNSIGNED NOT NULL,"                                     +
                  "FOREIGN KEY (ip_id) REFERENCES ip(id) ON DELETE CASCADE,"         + 
                  "FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE,"   + 
                  "PRIMARY KEY (id)"                                                 +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE dst_ip("                                             + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "query_id INT UNSIGNED NOT NULL,"                                  +
                  "ip_id INT UNSIGNED NOT NULL,"                                     +
                  "FOREIGN KEY (ip_id) REFERENCES ip(id) ON DELETE CASCADE,"         + 
                  "FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE,"   + 
                  "PRIMARY KEY (id)"                                                 +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE port("                                               + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "port INT UNSIGNED NOT NULL,"                                      +
                  "PRIMARY KEY (id)"                                                 +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE src_port("                                           + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "query_id INT UNSIGNED NOT NULL,"                                  +
                  "port_id INT UNSIGNED NOT NULL,"                                   +
                  "FOREIGN KEY (port_id) REFERENCES port(id) ON DELETE CASCADE,"     +
                  "FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE,"   +
                  "PRIMARY KEY (id)"                                                 +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE dst_port("                                           + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "query_id INT UNSIGNED NOT NULL,"                                  +
                  "port_id INT UNSIGNED NOT NULL,"                                   +
                  "FOREIGN KEY (port_id) REFERENCES port(id) ON DELETE CASCADE,"     +
                  "FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE,"   +
                  "PRIMARY KEY (id)"                                                 +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE proto("                                              + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "query_id INT UNSIGNED NOT NULL,"                                  +
                  "proto VARCHAR(3) NOT NULL,"                                       +
                  "PRIMARY KEY (id),"                                                +
                  "FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE"    +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE protocol_version("                                   + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "query_id INT UNSIGNED NOT NULL,"                                  +
                  "protocol_version VARCHAR(4) NOT NULL,"                            +
                  "PRIMARY KEY (id),"                                                +
                  "FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE"    +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE packets("                                            + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "query_id INT UNSIGNED NOT NULL,"                                  +
                  "packets INT UNSIGNED NOT NULL,"                                   +
                  "PRIMARY KEY (id),"                                                +
                  "FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE"    +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE bytes("                                              + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "query_id INT UNSIGNED NOT NULL,"                                  +
                  "bytes INT UNSIGNED NOT NULL,"                                     +
                  "PRIMARY KEY (id),"                                                +
                  "FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE"    +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE bps("                                                + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "query_id INT UNSIGNED NOT NULL,"                                  +
                  "bps INT UNSIGNED NOT NULL,"                                       +
                  "PRIMARY KEY (id),"                                                +
                  "FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE"    +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE pps("                                                + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "query_id INT UNSIGNED NOT NULL,"                                  +
                  "bps INT UNSIGNED NOT NULL,"                                       +
                  "PRIMARY KEY (id),"                                                +
                  "FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE"    +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE bpp("                                                + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "query_id INT UNSIGNED NOT NULL,"                                  +
                  "bpp INT UNSIGNED NOT NULL,"                                       +
                  "PRIMARY KEY (id),"                                                +
                  "FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE"    +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE duration("                                           + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "query_id INT UNSIGNED NOT NULL,"                                  +
                  "duration INT UNSIGNED NOT NULL,"                                  +
                  "PRIMARY KEY (id),"                                                +
                  "FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE"    +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE tos("                                                + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "query_id INT UNSIGNED NOT NULL,"                                  +
                  "tos TINYINT UNSIGNED NOT NULL,"                                   +
                  "PRIMARY KEY (id),"                                                +
                  "FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE"    +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE flags("                                              + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "query_id INT UNSIGNED NOT NULL,"                                  +
                  "flags VARCHAR(20) NOT NULL,"                                       +
                  "PRIMARY KEY (id),"                                                +
                  "FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE"    +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE scale("                                              + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "query_id INT UNSIGNED NOT NULL,"                                  +
                  "scale VARCHAR(1) NOT NULL,"                                       +
                  "PRIMARY KEY (id),"                                                +
                  "FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE"    +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE asn("                                                + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "query_id INT UNSIGNED NOT NULL,"                                  +
                  "asn VARCHAR(20) NOT NULL,"                                        +
                  "PRIMARY KEY (id),"                                                +
                  "FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE"    +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )

    store.execute(
                  "CREATE TABLE statistics("                                         + 
                  "id INT UNSIGNED NOT NULL AUTO_INCREMENT,"                         +
                  "query_id INT UNSIGNED NOT NULL,"                                  +
                  "plugin_id INT UNSIGNED NOT NULL,"                                 +
                  "number_of_flows INT UNSIGNED NOT NULL,"                           +
                  "number_of_bytes INT UNSIGNED NOT NULL,"                           +
                  "number_of_packets INT UNSIGNED NOT NULL,"                         +
                  "time_window VARCHAR(10) NOT NULL,"                                +
                  "PRIMARY KEY (id),"                                                +
                  "FOREIGN KEY (query_id) REFERENCES query(id) ON DELETE CASCADE,"   +
                  "FOREIGN KEY (plugin_id) REFERENCES plugin(id) ON DELETE CASCADE"  +
                  ")ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"
                 )


def insert_threats(store):

    #import logger
    from models import Threat
    threat_list = ['Generic', 'Other', 'Botnet', 'Malware', 'Spam', 'Phishing', 'DNSBL', 'Worm', 'Honeypot' ]

    for name in threat_list:
        threat = Threat()
        threat.type = unicode(name)
        store.add(threat)
        store.flush()
    store.commit()
    #logger.info('Threat list is inserted into database.')
    print('Threat list is inserted into database.')


def get_store(conf=None):
    '''
        Create and return a database connection if not exists yet.
    '''
    global __store
    if not __store:
        if conf is None:
            print 'initiate the db first'
            sys.exit(1)
        else:
            try:
                db = 'mysql://' + conf.db_user  + ':' + conf.db_password + '@' + conf.db_host + '/' + conf.db_name
                #db = "mysql://test@localhost/test"
                database = create_database(db)
                __store = Store(database)
                # Check if table exists
                result = __store.execute("SELECT version FROM application")
                if result:
                    print 'connection established'
                    return __store
            except MySQLException, e:
                if e.args[0] == 1146:
                    print 'Creating the tables'
                    initialize_db(__store)
                    insert_threats(__store)
                    return __store
                else:
                    print 'Another mysql error is happened'
                    print e
            except Exception, e:
                print e
                sys.exit()
    else:
        return __store



