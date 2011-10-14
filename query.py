#!/usr/local/bin/python

import sys
import socket, struct
import MySQLdb

# nfquery import
from nfquery import db

# temporary imports
from pprint import pprint


__all__ = ['query']


# ------------------------------------------------------------ ##
# IP address manipulation functions                             #
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
        Query class for storing etracted information from sources.
        
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

        output               : The list of the output_type information. If you set output_type as 1 you must provide
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
            Assign initial values of the query.
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


    ## ------------------------------------------------------------ ##
    ##                      INSERT FUNCTIONS                        ##
    ## ------------------------------------------------------------ ##
    def insert_query(self):
        '''
            Insert query information to database.

            = Source Check =
            
            Source related information should be registered to Query Server in the configuration file or from the web interface. 
            We will check if it exists in the source table before inserting the parsed information. not surce_name but source_id 
            could be given as a parameter to create_query function, then we can check source_id below. 
            That means source id, name, description and link should be configurable from the web interface.
            
            = Threat Check =
            
            Check threat type and threat name to insert into database tables. By default, a threat type is recorded without a threat name.
            Then for new threat names for this threat type, it is inserted with another id.

            = Insert Query =

            Inserts parsed query information to database. Parameter check is done by the query class constructor.

            = Output Check =

            Check output type and call the appropriate function.

            
        '''
        
        cursor = 

        # Begin with try to catch database exceptions.
        try:
            # Check if we have this source or not.
            statement = """select source_id from source where source_name=%s""" % (self.source_name) 
            cursor.execute(statement)
            source_id = cursor.fetchone()
            if source_id is None:
                sys.exit("Wrong source name is given! Please check if you give one of the source names published in the NfQuery Web Site" )
            
            # Check if we have this threat type or not.
            statement = """select threat_id from threat where threat_type=%s""" % (self.threat_type)
            cursor.execute( )
            threat_id = cursor.fetchone()
            if threat_id is None:
                sys.exit( "Wrong threat type is given! Please check if you give one of the threat types published in the NfQuery Web Site" )
            # Check if we have the given threat name for this threat type.
            elif self.threat_name is not None:
                statement = """select threat_id from threat where threat_name=%s and threat_type=%s""" % (self.threat_name, self.threat_type)
                cursor.execute(statement) 
                threat_id = cursor.fetchone()
                if threat_id is None:
                    # Add new threat name for this threat type.
                    cursor.execute("insert into threat (threat_type,threat_name) values('" + self.threat_type + "','" + self.threat_name + "')")
                    threat_id = (cursor.lastrowid,)
            # Threat name is not given, get the threat type id.
            else: 
                cursor.execute("select threat_id from threat where threat_type='" + self.threat_type + "' and threat_name IS NULL")
                threat_id = (cursor.lastrowid,)
            
            # Query Creation 
            statement = """ insert into query (source_id, threat_id, creation_time, query_type) values( %ld, %ld, %s, %d) """ % (source_id[0], threat_id[0], self.creation_time, self.output_type)
            cursor.execute(statement) 
            query_id=(cursor.lastrowid,)

        except MySQLdb.OperationalError, e:
            connection.rollback()
            sys.exit("Error %d: %s" % (e.args[0],e.args[1]))
        
        # Check output type and call the appropriate function.
        if self.output_type is 1:
            self.insert_ip_query(cursor, query_id)
        elif self.output_type is 2:
            self.insert_domain_query(cursor, query_id)
        else:
            self.insert_port_query(cursor, query_id)

        end_database_cursor()
     
    def insert_ip_query(self,cursor,query_id):
        '''
            Insert ip query to database.

            It uses dottedQuadToNum function to convert decimal dotted quad string to long integer.
        '''
        for ip in self.output.split(' '):
            
            # Calculate the decimal type of ip and check if we already have it
            ip_int = dottedQuadToNum(ip)

            try:
                # Check if we already have this ip.
                statement="""select ip_id from ip where ip_int=%ld""" % (ip_int)
                cursor.execute(statement)
                ip_id = cursor.fetchone()
                # Insert new ip.
                if ip_id is None:
                    statement = """ insert into ip (ip, ip_int) values(%s,%ld)""" % (ip, ip_int)
                    cursor.execute(statement)
                    ip_id=(cursor.lastrowid,)
                # Create query-ip relation
                statement = """ insert into query_ip (query_id, ip_id) values(%ld,%ld)""" % (query_id[0], ip_id[0]) 
                cursor.execute(statement)
                print 'query is inserted successfully!\n'

            except MySQLdb.OperationalError, e:
                connection.rollback()
                sys.exit("Error %d: %s" % (e.args[0],e.args[1])) 
         
 

    def insert_domain_query(self,cursor):
        '''
            Insert domain query to database.
        '''

        cursor.execute("insert into query values('" + source_id + "','" + threat_id + "','" + creation_time + "','" + self.output_type + "')" )
        query_id=cursor.fetchone()

        for domain in output.split(' '):
            # Check if we already have this ip
            cursor.execute("select domain_id from domain where domain='" + domain + "'")
            if domain_id is None:
                pass
                # So insert this new domain
            #    insert into domain values(domain)
            #    domain_id=cursor.fetchone()
            #
            #
            #insert into query_ip values(query_id, ip_id)


    def insert_port_query(self,cursor):
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
            statement = """select * from source where source_name=%s""" % (self.source_name) 
            cursor.execute(statement)
            source_id = cursor.fetchone()
            if source_id is None:
                sys.exit("Wrong source name is given! Please check if you give one of the source names published in the NfQuery Web Site" )
            
            # Check if we have this threat type or not.
            statement = """select threat_id from threat where threat_type=%s""" % (self.threat_type)
            cursor.execute( )
            threat_id = cursor.fetchone()
        except Exception:
            print 'exception happened'


    def print_content(self):
        '''
            Print content of the query attributes.
        ''' 
        print self.source_name + self.source_desc + self.source_link + self.threat_type + str(self.threat_name) + str(self.output_type) + self.output + self.creation_time + '\n'







