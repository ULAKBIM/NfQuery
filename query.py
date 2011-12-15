#!/usr/local/bin/python

import sys
import socket, struct
import MySQLdb
import hashlib

# nfquery import
from db import *


__all__ = ['query']


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
        
        source_name          : Name of the security source
                               example source_name : "Amada"
                               example source_name : "DFN-NREN"
                               example source_name : "ULAKBIM-NREN"

        source_desc          : Descrioption of the security source name
                               example source_name : "Amada C&C IP Blocklist"
                               example source_desc : "DFN NREN Honeypot"
                               example source_desc : "ULAKBIM NREN Blacklist"

        source_link          : Download link of the security source
                               example source_link : "http://amada.abuse.ch/blocklist.php?download=ipblocklist" 

        threat_type          : Type of the given threat information. Threat type must be one of the 
                               threat types which are published in nfquery website. Malware, Botnet, Spam, DoS, Virus, 
                               DNSBlacklist are main example threat types. Other kind of information is default ignored.
                               
 
        threat_name          : Name of the given threat. It is optional. Threat name can be the name of any malware,
                               botnet or other type of threats indicated in threat_type variable. Example threat names 
                               can be seen below. 
                               example threat_name : "Spyeye"
                               example threat_name : "Fake-AV"

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
    
    
        creation_time        : Time of the query creation.
                               example creation_time : "01.04.2011"
    
    '''

    
    def __init__(self, source_name, source_desc, source_link, threat_type, threat_name, output_type, output, creation_time):
        '''
            Assign initial VALUES of the query.
        '''
        if (not (4>output_type>0)):
            sys.exit('output_type must be between 1-3, please look at the definition.\n')
        self.source_name = source_name
        self.source_desc = source_desc
        self.source_link = source_link
        self.threat_type = threat_type
        self.threat_name = threat_name
        self.output_type = output_type
        self.output = output
        self.creation_time = creation_time
        # get the hash of output_list to INSERT INTO query table
        m = hashlib.md5()
        m.update(self.output)
        self.hash_value = m.hexdigest()


    ## ------------------------------------------------------------ ##
    ##                      INSERT FUNCTIONS                        ##
    ## ------------------------------------------------------------ ##

    # 1) code maintain edilmesi lazim
    # 2) print statementlarin logging e donusturulmesi lazim.

    def insert_query(self):
        '''
            Insert query information to database.

            = Source Check =
            
            Source related information should be registered to Query Server in the configuration file or FROM the web interface. 
            We will check if it exists in the source table before inserting the parsed information. not surce_name but source_id 
            could be given as a parameter to create_query function, then we can check source_id below. 
            That means source id, name, description and link should be configurable FROM the web interface.
            
            = Threat Check =
            
            Check threat type and threat name to INSERT INTO database tables. By default, a threat type is recorded without a threat name.
            Then for new threat names for this threat type, it is inserted with another id.

            = Insert Query =

            Inserts parsed query information to database. Parameter check is done by the query class constructor.

            = Output Check =

            Check output type and call the appropriate function.
        '''
        
        connection = db.get_database_connection()
        cursor = connection.cursor()

        # BU KISMI YENI SOURCE_THREAT_RELATION TABLOSUNA GORE TEKRAR YAZALIM,
        # HASH_VALUE ' YA GORE QUERY YI UPDATE EDIP ETMEYECEGIMIZE KARAR VERELIM.

        # Begin with try to catch database exceptions.
        new_query_flag=0
        try:
            # Check if we have this source or not.
            statement = """SELECT source_id FROM source WHERE source_name='%s'""" % (self.source_name)
            cursor.execute(statement)
            source_id = cursor.fetchone()
            if source_id is None:
                sys.exit("Wrong source name is given! Please check if you give one of the source names published in the NfQuery Web Site" )
            
            # Check if we have this threat type or not.
            statement = """SELECT threat_id FROM threat WHERE threat_type='%s'""" % (self.threat_type)
            cursor.execute(statement)
            threat_id = cursor.fetchone()
            if threat_id is None:
                sys.exit( "Wrong threat type is given! Please check if you give one of the threat types published in the NfQuery Web Site" )
            # Check if we have the given threat name for this threat type.
            elif self.threat_name is not None:
                statement = """SELECT threat_id FROM threat WHERE threat_name='%s' AND threat_type='%s'""" % (self.threat_name, self.threat_type)
                cursor.execute(statement) 
                threat_id = cursor.fetchone()
                if threat_id is None:
                    # Add new threat name for this threat type.
                    cursor.execute("INSERT INTO threat (threat_type,threat_name) VALUES('" + self.threat_type + "','" + self.threat_name + "')")
                    threat_id = (cursor.lastrowid,)
                    new_query_flag=1
            # Threat name is not given, get the threat type id.
            else: 
                cursor.execute("SELECT threat_id FROM threat WHERE threat_type='" + self.threat_type + "' AND threat_name IS NULL")
                threat_id = (cursor.lastrowid,)
         
            # if new_query_flag is SET insert the new query.
            # this means we didn't insert such a query with this threat_id before.
            if new_query_flag:
                # source_threat relation check
                statement = """SELECT st_id FROM source_threat_relation WHERE source_id=%d AND threat_id=%d""" % (source_id[0], threat_id[0])
                cursor.execute(statement)
                st_id=cursor.fetchone()
                if not st_id:
                    # Query Creation 
                    statement = """INSERT INTO source_threat_relation (source_id, threat_id) VALUES( %d, %d)""" % (source_id[0], threat_id[0])
                    cursor.execute(statement)
                    print 'New source_threat relation inserted\n'
                statement = """ INSERT INTO query (source_id, threat_id, creation_time, query_type, hash_value) VALUES( %d, %d, '%s', %d, '%s') """ %  (source_id[0], threat_id[0], self.creation_time, self.output_type, self.hash_value)
                cursor.execute(statement)
                query_id=(cursor.lastrowid,)
                print 'New query inserted'
                print 'New query id is %d' % query_id 
                self.insert_query_ip(cursor, query_id)
            else:
                # If this is not a new query, it could be inserted and deleted in the past or it could exist now in the query table, 
                # so we should check the table for query.
                statement = """
                                SELECT query_id FROM query WHERE source_id=%d AND threat_id=%d
                            """ % (source_id[0], threat_id[0])
                cursor.execute(statement)
                query_id = cursor.fetchone()
                if query_id:
                    print 'Query exists'
                    statement = """SELECT hash_value FROM query WHERE query_id=%d""" % (query_id)
                    cursor.execute(statement)
                    hash_value = cursor.fetchone()
                    print 'hash_value=%s, self.hash = %s' % (hash_value, self.hash_value)
                    if hash_value[0] == self.hash_value:
                        print 'Query is not updated'
                    else:
                        statement = """
                                        UPDATE query SET hash_value='%s' WHERE query_id=%d
                                    """ % (self.hash_value, query_id[0])
                        print statement
                        cursor.execute(statement)
                        print 'Query is updated'
                        print 'Updated query id is %d' % query_id 
                        self.insert_query_ip(cursor, query_id)
                else:       
                    # insert the query 
                    statement = """ INSERT INTO query (source_id, threat_id, creation_time, query_type, hash_value) VALUES( %d, %d, '%s', %d, '%s')  """ % (source_id[0], threat_id[0], self.creation_time, self.output_type, self.hash_value)
                    cursor.execute(statement)
                    query_id=(cursor.lastrowid,)
                    print 'New query inserted'
                    print 'New query id is %d' % query_id
                    self.insert_query_ip(cursor, query_id)

            cursor.close()
            db.give_database_connection()
        except MySQLdb.OperationalError, e:
            connection.rollback()
            sys.exit("Error %d: %s" % (e.args[0],e.args[1]))
        
        # THIS PART WILL EXIST IF AN OUTPUT TYPE WILL BE OR NOT?
        # Check output type and call the appropriate function.
        #if self.output_type is 1:
        #    self.insert_query_ip(cursor, query_id)
        #elif self.output_type is 2:
        #    self.insert_query_domain(cursor, query_id)
        #else:
        #    self.insert_query_port(cursor, query_id)
        
        
        
    def insert_query_ip(self, cursor, query_id):
        '''
            Insert ip query to database.
            It uses dottedQuadToNum function to convert decimal dotted quad string to long integer.
        '''
        for ip in self.output.split(' '):
            # Calculate the decimal type of ip and check if we already have it
            ip_int = dottedQuadToNum(ip)
            try:
                # Check if we already have this ip.
                statement="""SELECT ip_id FROM ip WHERE ip_int=%ld""" % (ip_int)
                cursor.execute(statement)
                ip_id = cursor.fetchone()
                # Insert new ip.
                if ip_id is None:
                    statement = """ INSERT INTO ip (ip, ip_int) VALUES('%s',%ld)""" % (ip, ip_int)
                    cursor.execute(statement)
                    ip_id=(cursor.lastrowid,)
                # Create query-ip relation
                statement = """ INSERT INTO query_ip (query_id, ip_id) VALUES(%ld,%ld)""" % (query_id[0], ip_id[0]) 
                cursor.execute(statement)
                print statement
            except MySQLdb.OperationalError, e:
                connection.rollback()
                sys.exit("Error %d: %s" % (e.args[0],e.args[1])) 
         
 

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
                sys.exit("Wrong source name is given! Please check if you give one of the source names published in the NfQuery Web Site" )
            
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
        print self.source_name + '\n' + self.source_desc + '\n' + self.source_link + '\n' + self.threat_type + '\n' + str(self.threat_name) + '\n' + str(self.output_type) + '\n' + self.output + '\n' + self.creation_time + '\n' 


