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
        protocol_version = protocol = tos = packets = bytes_ = None
        if parsername is None:
            self.qglogger.warning('Parser name is none')
            return
        else:
            for index in range(len(self.sources)):
                if parsername == self.sources[index].parser:
                    data = self.validateParserOutput(self.sources[index].outputfile)
                    if data: 
                        ### BURAYI ASAGIYA TASIYALIM, PARAMETRE SADECE data olsun, 
                            if key == 'protocol_version':
                                protocol_version = data[key]
                            elif key == 'protocol':
                                protocol = data[key]
                            elif key == 'tos':
                                tos = data[key]
                            elif key == 'packets':
                                packets = data[key]
                            elif key == 'bytes':
                                bytes_ = data[key]
                        self.insertQuery( data['source_name'], data['output_type'], data['output'], data['update_time'],
                                          protocol_version=protocol_version, protocol=protocol, tos=tos, packets=packets, 
                                          bytes_=bytes_ )
                        return
                    else:
                        self.qglogger.warning('Parser output validation returned bad.')
                        return

    def validateParserOutput(self, outputfile):
        '''
            Check parser output values and necessary keys.
            Returns validated output.
        '''
        options = [ 'source_name', 'output_type', 'output', 'update_time' ] 
        filters = [ 'protocol_version', 'protocol', 'tos', 'packets', 'bytes' ]
        try:
            outputfile = open(outputfile, 'r')
            data = json.load(outputfile)
            outputfile.close()
            #self.qglogger.debug('%s, %s, %s ' % (data['source_name'], data['update_time'], data['output']))
            if (set(options).issubset(set(data.keys()))):
                source = self.store.find(Source, Source.name == unicode(data['source_name']))
                if source.is_empty():
                    self.qglogger.warning('Source name : %s is not found in the database' % data['source_name'])
                    self.qglogger.warning('Please check your parser output %s' % outputfile)
                    return
                elif not(0 < data['output_type'] < 4):
                    qglogger.warning('Output type value : %d is not correct' % data['output_type'])
                    qglogger.warning('Please check your parser output %s' % outputfile)
                    return
                elif set(data.keys()).issubset(set(options + filters)):
                    print data.keys()
                    self.qglogger.debug('Output of parser is valid')
                    return data
                else:
                    self.qglogger.warning('Unknown filter is found in parser output %s' % outputfile)
                    return
            self.qglogger.warning('Mandatory keys are not found in parser output %s' % outputfile)
            return
        except Exception, e:
            self.qglogger.warning('got exception: %r' % (e))
            self.qglogger.warning('Output is not loaded correctly, check parser output : %s' % outputfile)
            return

            
    def insertQuery(self, source_name, output_type, output, update_time, 
                          protocol_version=None, protocol=None, tos=None, packets=None, bytes_=None):
        '''
           Inserts query information to database. 
           To tables :  
                     1) query, query_ip and ip
                     2) query, query_domain and domain                      
                     3) query, query_port and port
                     and finally to :
                     - filters   
        '''
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        source_id = self.store.find(Source.id, Source.name == unicode(source_name)).one()
        if source_id is None:
            self.qglogger.error('Source : %s is not found in the database' % source_name)
            self.qglogger.error('Please reconfigure your sources, or check the parser')
            return 
        # get the hash of output to check if the query is updated.
        md5hash = hashlib.md5()
        md5hash.update(output + protocol_version + protocol + str(tos) + str(packets) + str(bytes_))
        checksum = md5hash.hexdigest()
        query_id = self.store.find(Query.id, Query.source_id == source_id).one()
        if query_id is None:
            '''
                Adding new query
            '''
            query = Query()
            query.source_id     = source_id
            query.type          = output_type
            query.checksum      = unicode(checksum)
            query.creation_time = unicode(update_time)
            self.store.add(query)
            self.store.flush()
            filters = Filter()
            filters.query_id = query.id
            filters.protocol_version = unicode(protocol_version)
            filters.protocol = unicode(protocol)
            filters.tos = tos
            filters.packets = packets
            filters.bytes = bytes_
            self.store.add(filters)
            self.store.flush()
            if query.type == 1:                           # means output gives only ip information
                self.insertIPQuery(query.id, output)
            elif query.type == 2:                         # means output gives only port information
                self.insertPortQuery(query.id, output)
            elif query.type == 3:                         # means output gives only ip-port information
                self.insertIPPortQuery(query.id, output)
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
                query = self.store.find(Query, Query.id == query_id).one()
                if query.type != output_type:
                    self.qglogger.error('Source output_type is changed')
                    self.qglogger.error('Query can not be updated!')
                    self.store.rollback()
                    return
                query.type = output_type
                query.checksum = unicode(checksum)
                query.update_time = unicode(update_time)
                filters = self.store.find(Filter, Filter.query_id == query.id)
                filters.protocol_version = unicode(protocol_version)
                filters.protocol = unicode(protocol)
                filters.tos = tos
                filters.packets = packets
                filters.bytes = bytes_
                self.store.add(filters)
                self.store.flush()
                if query.type == 1:                           # means output gives only ip information
                    self.insertIPQuery(query.id, output)
                elif query.type == 2:                         # means output gives only port information
                    self.insertPortQuery(query.id, output)
                elif query.type == 3:                         # means output gives only ip-port information
                    self.insertIPPortQuery(query.id, output)
                self.qglogger.debug('Query is updated.')
            elif checksum is None:
                ''' 
                   Fatal Error
                '''
                self.qglogger.error('Fatal Error : checksum is None')
        self.store.commit()

        
    def insertIPQuery(self, query_id, ip_list):
        '''
            Insert ip query to database.
        '''
        qid = query_id
        for ip in ip_list.split(' '):
            # Calculate the decimal type of ip and check if we already have it
            if ip is not ' ' and ip is not '':
                ip_int = dottedQuadToNum(ip)
                # Check if we already have this ip.
                ip_id = self.store.find(IP.id, IP.ip_int == ip_int).one()
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
                    relation.ip_id = ip_obj.id
                    self.store.add(relation)
                    self.store.flush()
                    self.qglogger.debug('New query-ip relation is added')
                else:
                    self.qglogger.debug('We already have this ip')
                    # Check if we already have this ip-query relation
                    qp_id = self.store.find(QueryIP.id, (QueryIP.query_id == qid) & (QueryIP.ip_id == ip_id))
                    if qp_id is not None:
                        self.qglogger.debug('We already have this query-ip relation')
                    else:
                        # Create query-ip relation
                        relation = QueryIP()
                        relation.query_id = qid
                        relation.ip_id = ip_id
                        self.qglogger.debug('New query-ip relation is added')
 

    #def insertPortQuery(self, query_id, port_list):
    #    '''
    #        Insert port query to database.
    #    '''
    #    qid = query_id
    #    for port in port_list.split(' '):
    #        # Check if port consists of digits
    #        if port.isdigit():
    #            # Check if we already have this port.
    #            port_id = self.store.find(Port.id, Port.port == port).one()
    #            if ip_id is None:
    #                # Insert new port and query-port relation.
    #                port_obj = Port()
    #                port_obj.port = int(port)
    #                self.store.add(port_obj)
    #                self.store.flush()
    #                self.qglogger.debug('New port is added')
    #                relation = QueryPort()
    #                relation.query_id = qid
    #                relation.port_id = port_obj.id
    #                self.store.add(relation)
    #                self.store.flush()
    #                self.qglogger.debug('New query-port relation is added')
    #            else:
    #                self.qglogger.debug('We already have this port')
    #                # Check if we already have this port-query relation
    #                qpo_id = self.store.find(QueryPort.id, (QueryPort.query_id == qid) & (QueryPort.port_id == port_id))
    #                if qp_id is not None:
    #                    self.qglogger.debug('We already have this query-port relation')
    #                else:
    #                    # Create query-port relation
    #                    relation = QueryPort()
    #                    relation.query_id = qid
    #                    relation.port_id = port_id
    #                    self.qglogger.debug('New query-port relation is added')


    def createQueryFilterExpressions(self):
        pass
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
        
        #expr = ''
        #query_list = self.store.find(Query)
        #if not query_list.is_empty():
        #    for query in query_list:
        #        '''
        #            'checksum', 'creation_time', 'query_id', 'query_type', 'source', 'source_id', 'update_time'
        #        '''
        #        if not query.ip_id == '':
        #            
        #        if not query.type









    def createQueryFromStatistics(self):
        pass




