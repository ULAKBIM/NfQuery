#!/usr/local/bin/python

import sys
import socket, struct
#from MySQLdb import DatabaseError
import logging
import hashlib

# nfquery import
import nfquery
from db2 import db2
from logger import createLogger
from models import Source, Query, IP, QueryIP
from utils import dottedQuadToNum

class query:
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
        '''
            Start logging and assign query values
        '''
        self.qlogger = createLogger('Query')
        self.source_name = source_name
        self.output_type = output_type
        self.output = output
        self.update_time = update_time         # if first, it's creation_time
        m = hashlib.md5()                      # get the hash of output to check if the query is updated. 
        m.update(self.output)
        self.checksum = m.hexdigest()
        
        
    def insert_query(self, store):
        '''
           Inserts query information to database. 
           To tables :  
                     1) query, query_ip and ip
                     2) query, query_domain and domain                      
                     3) query, query_port and port
        '''
        self.qlogger.debug('In %s' % sys._getframe().f_code.co_name)
        source_id = store.find(Source.source_id, Source.source_name== unicode(self.source_name)).one()
        if source_id is None:
            self.qlogger.error('%s is not found in the database' % self.source_name)
            self.qlogger.error('Please reconfigure your sources, or check the parser')
        query_id = store.find(Query.query_id, Query.source_id == source_id).one()
        if query_id is None:
            '''
                Adding new query
            '''
            query = Query()
            query.source_id = source_id
            query.query_type = self.output_type
            query.checksum = unicode(self.checksum)
            query.creation_time = unicode(self.update_time)
            store.add(query)
            store.flush()
            self.qlogger.debug('New query is added')
            self.insert_query_ip(store, query.query_id)
            self.qlogger.info('New query is inserted succesfully')
        else:
            checksum = store.find(Query.checksum, Query.source_id == source_id).one()
            if checksum == self.checksum:
                '''
                    Don't update this query
                '''
                self.qlogger.debug('Query is not updated.')
            elif checksum != self.checksum:
                '''
                    Update query
                '''
                query = store.find(Query, Query.query_id == query_id).one()
                query.query_type = self.output_type
                query.checksum = unicode(self.checksum)
                query.update_time = unicode(self.update_time)
                self.insert_query_ip(store, query.query_id)
                self.qlogger.debug('Query is updated.')
            elif checksum is None:
                ''' 
                   Fatal Error
                '''
                self.qlogger.error('Fatal Error : checksum is None')
        store.commit()

        
    def insert_query_ip(self, store, query_id):
        '''
            Insert ip query to database.
        '''
        for ip in self.output.split(' '):
            # Calculate the decimal type of ip and check if we already have it
            if ip is not ' ' and ip is not '':
                ip_int = dottedQuadToNum(ip)
                # Check if we already have this ip.
                ip_id = store.find(IP.ip_id, IP.ip_int == ip_int).one()
                if ip_id is None:
                    # Insert new ip and query-ip relation.
                    ip_obj = IP()
                    ip_obj.ip = unicode(ip)
                    ip_obj.ip_int = ip_int
                    store.add(ip_obj)
                    store.flush()
                    self.qlogger.debug('New ip is added')
                    relation = QueryIP()
                    relation.query_id = query_id
                    relation.ip_id = ip_obj.ip_id
                    store.add(relation)
                    store.flush()
                    self.qlogger.debug('New query-ip relation is added')
                else:
                    self.qlogger.debug('We already have this ip')
                    # Check if we already have this ip-query relation
                    qp_id = store.find(QueryIP.qp_id, (QueryIP.query_id == query_id) & (QueryIP.ip_id == ip_id))
                    if qp_id is not None:
                        self.qlogger.debug('We already have this query-ip relation')
                    else:
                        # Create query-ip relation
                        relation = QueryIP()
                        relation.query_id = query_id
                        relation.ip_id = ip_id
                        self.qlogger.debug('New query-ip relation is added')
 

    def insert_query_domain(self,cursor):
        '''
            Insert domain query to database.
        '''
        pass
        #cursor.execute("INSERT INTO query VALUES('" + source_id + "','" + threat_id + "','" + creation_time + "','" + self.output_type + "')" )
        #query_id=cursor.fetchone()

        #for domain in output.split(' '):
        #    # Check if we already have this ip
        #    cursor.execute("SELECT domain_id FROM domain WHERE domain='" + domain + "'")
        #    if domain_id is None:
        #        pass
        #        # So insert this new domain
        #    #    INSERT INTO domain VALUES(domain)
        #    #    domain_id=cursor.fetchone()
        #    #
        #    #
        #    #INSERT INTO query_ip VALUES(query_id, ip_id)


    def insert_query_port(self,cursor):
        '''
            Insert port query to database.
        '''
        pass


