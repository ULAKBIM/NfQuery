#!/usr/local/bin/python

import sys
import socket, struct
from MySQLdb import DatabaseError
import logging
import hashlib

# nfquery import
from db import db
from defaults import defaults
from logger import ColoredLogger


# ------------------------------------------------------------ ##
# IP address manipulation functions                             #
# It should be in another file                                  #
                                                                #
def dottedQuadToNum(ip):                                        #
    "convert decimal dotted quad string to long integer"        #
    hexn = ''.join(["%02X" % long(i) for i in ip.split('.')])   #
    return long(hexn, 16)                                       #
                                                                #
def numToDottedQuad(n):                                         #
    "convert long int to dotted quad string"                    #
                                                                #
    d = 256 * 256 * 256                                         #
    q = []                                                      #
    while d > 0:                                                #
        m,n = divmod(n,d)                                       #
        q.append(str(m))                                        #
        d = d/256                                               #
                                                                #
    return '.'.join(q)                                          #
# ------------------------------------------------------------ ##


class query():
    '''
        Query class for storing etracted information FROM sources.
        
        source_id            : id of the security source

        output_type          : Type of the given list information provided by that source. output_type must be a number 
                               between 1-3. Meaning of the numbers can be seen below.

                                   1 : IP List
                                   2 : Domain List
                                   3 : Port List

        output               : The list of the output_type information. If you SET output_type as 1 you must provide
                               an IP List and so on for other options.
                               Examples of output can be seen below.
    
                               example IP List output: ['109.235.251.49 109.235.251.51 109.235.251.54 109.235.251.57 178.238.227.10']
    
                               example Domain List output: ['0o0o0o0o0.com 19js810300z.com 1efmdfieha-mff.com 1iii1i11i1ii.com 1zabslwvn538n4i5tcjl.com']
    
                               example Port List output: ['58470 58443 58439 58431 58427 58419 58417 58411 58398 58389']
    
        update_time          : Last update time of the query.
                               example update_time : "01.04.2011/14:22"

    '''
    
    def __init__(self, source_name, output_type, output, update_time=None):
        '''Start logging and assign default values'''
        logging.setLoggerClass(ColoredLogger)        
        self.qlogger = logging.getLogger('Query')
        self.qlogger.setLevel(defaults.loglevel)
        self.source_name = source_name
        self.output_type = output_type
        self.output = output
        self.update_time = update_time         # if first, it's creation_time
        m = hashlib.md5()        # get the hash of output to check if the query is updated. 
        m.update(self.output)
        self.hash_value = m.hexdigest()
        #print self.hash_value
        
        
    def insert_query(self):
        '''
            Inserts query information to database. 
            To tables query, query_ip and ip

            query
            +---------------+----------------------+------+-----+---------+----------------+
            | query_id    | int(10) unsigned     | NO   | PRI | NULL    | auto_increment   |        
            | source_id   | int(10) unsigned     | NO   | MUL | NULL    |                  |
            | update_time | varchar(20)          | YES  |     | NULL    |                  |        # update time
            | query_type  | smallint(5) unsigned | NO   |     | NULL    |                  |        # ip,domain,port,ip+port 
            | hash_value  | varchar(32)          | NO   |     | NULL    |                  |        # hash value of this query    
            +---------------+----------------------+------+-----+---------+----------------+

            query_ip
            +----------+------------------+------+-----+---------+----------------+
            | qp_id    | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
            | query_id | int(10) unsigned | NO   | MUL | NULL    |                |
            | ip_id    | int(10) unsigned | NO   | MUL | NULL    |                |
            +----------+------------------+------+-----+---------+----------------+

            ip
            +--------+---------------------+------+-----+---------+----------------+
            | Field  | Type                | Null | Key | Default | Extra          |
            +--------+---------------------+------+-----+---------+----------------+
            | ip_id  | int(10) unsigned    | NO   | PRI | NULL    | auto_increment |
            | ip     | varchar(20)         | NO   |     | NULL    |                |
            | ip_int | bigint(20) unsigned | NO   |     | NULL    |                |
            +--------+---------------------+------+-----+---------+----------------+
        '''

        self.qlogger.debug('In %s' % sys._getframe().f_code.co_name)
        connection = db.get_database_connection()
        cursor = connection.cursor()
        #print connection
        #print cursor

        # Begin with try to catch database exceptions.
        try:
            # Check if we have this source or not.
            statement = """SELECT source_id FROM source WHERE source_name='%s'""" % (self.source_name)
            cursor.execute(statement)
            source_id = cursor.fetchone()
            if source_id is None:
                self.qlogger.error('Please reconfigure your sources, or check the parser')
                self.qlogger.error('%s is not found in the database' % self.source_name)
                return 1

            statement = """SELECT query_id FROM query WHERE source_id=%d""" % (source_id[0])
            cursor.execute(statement)
            query_id = cursor.fetchone()

            if query_id is None:
                '''Adding new query'''
                statement = """ INSERT INTO query (source_id, query_type, hash_value, creation_time) VALUES( %d, %d, '%s', '%s') """ % ( 
                                source_id[0], self.output_type, self.hash_value, self.update_time )
                cursor.execute(statement)
                query_id=(cursor.lastrowid,)
                self.insert_query_ip(cursor, query_id)
                print 'New query is added'
            else:
                statement = """ SELECT hash_value FROM query WHERE source_id=%d""" % source_id
                cursor.execute(statement)
                hash_value = cursor.fetchone()
                if hash_value[0] == self.hash_value:
                    '''Don't update this query'''
                    self.qlogger.info('No need to update this query')
                elif hash_value[0] != self.hash_value:
                    '''Update query'''
                    self.qlogger.info('Updating the query')
                    statement = """ UPDATE query SET query_type=%s, hash_value='%s', update_time='%s' WHERE query_id=%d """ % (self.output_type, self.hash_value, self.update_time, query_id[0])
                    cursor.execute(statement)
                    self.insert_query_ip(cursor, query_id)
                elif hash_value is None:
                    ''' Fatal Error'''
                    self.qlogger.error('Fatal Error : hash_value is None')
                    return 1
        except DatabaseError, e:
            connection.rollback()
            self.qlogger.error("Error %d: %s" % (e.args[0],e.args[1]))
            return 1
        #except MySQLdb.OperationalError, e:
        #    connection.rollback()
        #    self.qlogger.error("Error %d: %s" % (e.args[0],e.args[1]))
        #    return 1
        except Exception, e:
            connection.rollback()
            self.qlogger.error("Error %d: %s" % (e.args[0],e.args[1]))
            return 1

        
        cursor.close()                      
        db.sync_database_connection()
        return 0

        
    def insert_query_ip(self, cursor, query_id):
        '''
            Insert ip query to database.
            It uses dottedQuadToNum function to convert decimal dotted quad string to long integer.
        '''
        for ip in self.output.split(' '):
            # Calculate the decimal type of ip and check if we already have it
            if ip is not ' ' and ip is not '':
                ip_int = dottedQuadToNum(ip)
                try:
                    # Check if we already have this ip.
                    statement="""SELECT ip_id FROM ip WHERE ip_int=%ld""" % (ip_int)
                    #print statement
                    cursor.execute(statement)
                    ip_id = cursor.fetchone()
                    if ip_id is None:
                        # Insert new ip and query-ip relation.
                        statement = """ INSERT INTO ip (ip, ip_int) VALUES('%s',%ld)""" % (ip, ip_int)
                        cursor.execute(statement)
                        ip_id=(cursor.lastrowid,)
                        self.qlogger.debug('New ip is inserted')
                        statement = """ INSERT INTO query_ip (query_id, ip_id) VALUES(%ld,%ld)""" % (query_id[0], ip_id[0])
                        cursor.execute(statement)
                        self.qlogger.debug('New query-ip relation is inserted')
                    else:
                        # Check if we already have this ip-query relation
                        statement = """ SELECT qp_id FROM query_ip WHERE query_id=%d AND  ip_id=%d""" % (query_id[0], ip_id[0])
                        cursor.execute(statement)
                        qp_id = cursor.fetchone()
                        if qp_id is not None:
                            self.qlogger.debug('We already have this query-ip relation')
                        else:
                            # Create query-ip relation
                            statement = """ INSERT INTO query_ip (query_id, ip_id) VALUES(%ld,%ld)""" % (query_id[0], ip_id[0]) 
                            cursor.execute(statement)
                            self.qlogger.debug('New query-ip relation is inserted')
                except MySQLdb.OperationalError, e:
                    connection.rollback()
                    qlogger.error('Error %d: %s'  % (e.args[0],e.args[1]))
                    return 1
         
 

    def insert_query_domain(self,cursor):
        '''
            Insert domain query to database.
        '''
        cursor.execute("INSERT INTO query VALUES('" + source_id + "','" + threat_id + "','" + creation_time + "','" + self.output_type + "')" )
        query_id=cursor.fetchone()

        for domain in output.split(' '):
            # Check if we already have this ip
            cursor.execute("SELECT domain_id FROM domain WHERE domain='" + domain + "'")
            if domain_id is None:
                pass
                # So insert this new domain
            #    INSERT INTO domain VALUES(domain)
            #    domain_id=cursor.fetchone()
            #
            #
            #INSERT INTO query_ip VALUES(query_id, ip_id)


    def insert_query_port(self,cursor):
        '''
            Insert port query to database.
        '''
        pass

    ## ------------------------------------------------------------ ##
    ##                      GET FUNCTIONS                           ##
    ## ------------------------------------------------------------ ##
    def get_query_information(self):
        '''
            gets e query information
        '''
        
        cursor = get_database_cursor()

        # Begin with try to catch database exceptions.
        try:
            # Check if we have this source or not.
            statement = """SELECT * FROM source WHERE source_name=%s""" % (self.source_name) 
            cursor.execute(statement)
            source_id = cursor.fetchone()
            if source_id is None:
                self.qlogger.error("Wrong source name is given! Please check if you give one of the source names published in the NfQuery Web Site" )
                return 1
            
            # Check if we have this threat type or not.
            statement = """SELECT threat_id FROM threat WHERE threat_type=%s""" % (self.threat_type)
            cursor.execute( )
            threat_id = cursor.fetchone()
        except Exception:
            print 'exception happened'


    def print_content(self):
        '''
            Print content of the query attributes.
        ''' 
        print self.source_name + '\n' + '\n' + self.source_link + '\n' + self.threat_type + '\n' + str(self.threat_name) + '\n' + str(self.output_type) + '\n' + self.output + '\n' + self.creation_time + '\n' 


