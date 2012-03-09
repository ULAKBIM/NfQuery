#!/usr/local/bin/python

import simplejson as json
import logging
import sys
import os.path
import hashlib
import subprocess
import time

# nfquery imports
import db
import logger
from models import Query, QueryIP, IP, Source
from utils import *

__all__ = ['QueryGenerator']

class QueryGenerator:

    def __init__(self, sources):
        self.qglogger = logger.createLogger('querygenerator')
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.qglogger.info('Starting Query Generator')
        self.store = db.get_store()
        self.sources = sources

 
    def createQuery(self, parsername=None):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        if parsername is None:
            for index in range(len(self.sources)):
                try:
                    outputfile = open(self.sources[index].outputfile, 'r')
                    data = json.load(outputfile)
                    #self.qglogger.debug('%s, %s, %s ' % (data['source_name'], data['update_time'], data['output']))
                    outputfile.close()
                except Exception, e:
                    self.qglogger.warning('got exception: %r' % (e))
                    self.qglogger.warning('could not load output of parser %s' % self.sources[index].parser)
                    continue
                # Check values with db and conf file.
                # source_name, listtype, output and update time SYNTAX CHECK should be done here!!!!
                self.insertQuery(data['source_name'], data['output_type'], data['output'], data['update_time'])
        else:
            for index in range(len(self.sources)):
                if parsername == self.sources[index].parser:
                    try:
                        outputfile = open(self.sources[index].outputfile, 'r')
                        data = json.load(outputfile)
                        outputfile.close()
                    except Exception, e:
                        self.qglogger.warning('got exception: %r' % (e))
                        self.qglogger.warning('could not create queries for parser %s' % parsername)
                        continue
                    # Check values with db and conf file.
                    # source_name, outputtype, output and update time SYNTAX CHECK should be done here!!!!
                    self.insertQuery(data['source_name'], data['output_type'], data['output'], data['update_time'])

            
    def insertQuery(self, source_name, output_type, output, update_time):
        '''
           Inserts query information to database. 
           To tables :  
                     1) query, query_ip and ip
                     2) query, query_domain and domain                      
                     3) query, query_port and port
        '''
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        source_id = self.store.find(Source.source_id, Source.source_name== unicode(source_name)).one()
        if source_id is None:
            self.qglogger.error('%s is not found in the database' % source_name)
            self.qglogger.error('Please reconfigure your sources, or check the parser')
        
        # get the hash of output to check if the query is updated.
        md5hash = hashlib.md5()                      
        md5hash.update(output)
        checksum = md5hash.hexdigest() 

        query_id = self.store.find(Query.query_id, Query.source_id == source_id).one()
        if query_id is None:
            '''
                Adding new query
            '''
            query = Query()
            query.source_id     = source_id
            query.query_type    = output_type
            query.checksum      = unicode(checksum)
            query.creation_time = unicode(update_time)
            self.store.add(query)
            self.store.flush()
            if query.query_type == 1:                           # means output gives only ip information
                self.insertIPQuery(query.query_id, output)
            elif query.query_type == 2:                         # means output gives only port information
                self.insertPortQuery(query.query_id, output)
            elif query.query_type == 3:                         # means output gives only ip-port information
                self.insertIPPortQuery(query.query_id, output)
            else:
                self.qglogger.error('Check output_type in configuration file.')
                self.qglogger.error('New query is not inserted!')
                self.store.rollback()
                return
            self.qglogger.info('New query is inserted succesfully')
        else:
            dbchecksum = self.store.find(Query.checksum, Query.source_id == source_id).one()
            if dbchecksum == checksum:
                '''
                    Don't update this query
                '''
                self.qglogger.debug('Query is not updated.')
            elif dbchecksum != checksum:
                '''
                    Update query
                '''
                query = self.store.find(Query, Query.query_id == query_id).one()
                if query.query_type != output_type:
                    self.qglogger.error('Source output type is changed')
                    self.qglogger.error('Query can not be updated!')
                    self.store.rollback()
                    return
                query.query_type    = output_type
                query.checksum      = unicode(checksum)
                query.update_time   = unicode(update_time)
                self.insertQueryIP(query.query_id, output)
                self.qglogger.debug('Query is updated.')
            elif checksum is None:
                ''' 
                   Fatal Error
                '''
                self.qglogger.error('Fatal Error : checksum is None')
        self.store.commit()

        
    def insertQueryIP(self, query_id, ip_list):
        '''
            Insert ip query to database.
        '''
        qid = query_id
        for ip in ip_list.split(' '):
            # Calculate the decimal type of ip and check if we already have it
            if ip is not ' ' and ip is not '':
                ip_int = dottedQuadToNum(ip)
                # Check if we already have this ip.
                ip_id = self.store.find(IP.ip_id, IP.ip_int == ip_int).one()
                if ip_id is None:
                    # Insert new ip and query-ip relation.
                    ip_obj = IP()
                    ip_obj.ip = unicode(ip)
                    ip_obj.ip_int = ip_int
                    self.store.add(ip_obj)
                    self.store.flush()
                    self.qglogger.debug('New ip is added')
                    relation = QueryIP()
                    relation.query_id = qid
                    relation.ip_id = ip_obj.ip_id
                    self.store.add(relation)
                    self.store.flush()
                    self.qglogger.debug('New query-ip relation is added')
                else:
                    self.qglogger.debug('We already have this ip')
                    # Check if we already have this ip-query relation
                    qp_id = self.store.find(QueryIP.qp_id, (QueryIP.query_id == qid) & (QueryIP.ip_id == ip_id))
                    if qp_id is not None:
                        self.qglogger.debug('We already have this query-ip relation')
                    else:
                        # Create query-ip relation
                        relation = QueryIP()
                        relation.query_id = qid
                        relation.ip_id = ip_id
                        self.qglogger.debug('New query-ip relation is added')
 

    def createQueryFilterExpressions(self):
        # 1) Fetch all queries,
        # 2) Check what kind of fields the query have that will be  used as netflow filter arguments : 
        #       a) - ip (src-dst), port(src-dst), protocol, packets, bytes, start_time, end_time, etc... = Expression Part
        #       b) - time_interval = Execution 'nfdump -r /and/dir/nfcapd.200407110845' Part
        #       c) - order by =  Top N Statistics Part -> This part will show what we will parse as query executin result and send to QueryServer
        # 3) Create the expression with given parameters -> the most specific one
        #       a) - Create more general filters from already created filter with removing some options or assigning them to any,
        #            for example ;
        #                         if IP and PORT given -> the most spec filter expr: 'src ip IP src port PORT'
        #                         from this expr we'll create also : 'src ip IP src port ANY' and 'src ip ANY src port PORT'
        # 4) Concatenate produced filters like expr, expr, expr
        # 5) Once we have all the expr integrate them with other general parameters (time_interval, file, etc.)
        # 6) Put this information to db appropriately.
        # 7) ?

        expr = ''
        query_list = self.store.find(Query)
        if not query_list.is_empty():
            for query in query_list:
                '''
                    'checksum', 'creation_time', 'query_id', 'query_type', 'source', 'source_id', 'update_time'
                '''
                if not query.ip_id == '':
                    
                if not query.query_type











    def createQueryFromStatistics(self):
        pass
