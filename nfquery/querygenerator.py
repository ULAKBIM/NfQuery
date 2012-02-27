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
from models import *
from utils import *
from subscriptiongenerator import SubscriptionGenerator

__all__ = ['QueryGenerator']

class QueryGenerator:

    def __init__(self, sources):
        self.qglogger = logger.createLogger('querygenerator')
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.store = db.get_store()
        self.sources = sources

 
    def createQuery(self, parsername=None):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        if parsername is None:
            for index in range(len(self.sources)):
                try:
                    outputfile = open(self.sources[index].outputfile, 'r')
                    data = json.load(outputfile)
                    #self.qglogger.debug('%s, %s, %s ' % (data['source_name'], data['update_time'], data['ip_list']))
                    outputfile.close()
                except Exception, e:
                    self.qglogger.warning('got exception: %r' % (e))
                    self.qglogger.warning('could not load output of parser %s' % self.sources[index].parser)
                    continue
                # Check values with db and conf file.
                # source_name, listtype, output and update time check should be done here!!!!
                self.insertQuery(data['source_name'], data['output_type'], data['ip_list'], data['update_time'])
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
                    # source_name, outputtype, output and update time check should be done here!!!!
                    self.insertQuery(data['source_name'], data['output_type'], data['ip_list'], data['update_time'])

            
    def insertQuery(self, source_name, output_type, ip_list, update_time):
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
        md5hash.update(ip_list)
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
            self.qglogger.debug('New query is added')
            self.insertQueryIP(query.query_id, ip_list)
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
                query.query_type    = output_type
                query.checksum      = unicode(checksum)
                query.update_time   = unicode(update_time)
                self.insertQueryIP(query.query_id, ip_list)
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
 

