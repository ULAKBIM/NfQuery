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
from models import Query, QueryIP, IP, QueryPort, Port, QueryIPPort, IPPort, Filter, Source
from storm.locals import *
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
                        self.insertQuery(data)
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

            
    def insertQuery(self, data ):
    #def insertQuery(self, source_name, output_type, output, update_time, 
    #                      protocol_version=None, protocol=None, tos=None, packets=None, bytes_=None):
        '''
           Inserts query information to database. 
           To tables :  
                     1) query, query_ip and ip
                     2) query, query_domain and domain                      
                     3) query, query_port and port
                     and finally to :
                     - filters   
            Also, as parameter it gets data dictionary,
                - data has mandatory 4 keys which are : output, output_type, update_time, source_name
                - it may also have filters which are protocol, bytes, packets etc.
        '''
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        # get the hash of output to check if the query is updated.
        protocol_version=protocol=tos=packets=bytes_=None
        md5hash = hashlib.md5()
        md5hash.update(data['output'])
        for key in data.keys():
            if key == 'protocol_version':
                protocol_version = data[key]
                md5hash.update(protocol_version)
            elif key == 'protocol':
                protocol = data[key]
                md5hash.update(protocol)
            elif key == 'tos':
                tos = data[key]
                md5hash.update(str(tos))
            elif key == 'packets':
                packets = data[key]
                md5hash.update(str(packets))
            elif key == 'bytes':
                bytes_ = data[key]
                md5hash.update(str(bytes_))
        checksum = md5hash.hexdigest()
        
        source_id = self.store.find(Source.id, Source.name == unicode(data['source_name'])).one()
        if source_id is None:
            self.qglogger.error('Source : %s is not found in the database' % data['source_name'])
            self.qglogger.error('Please reconfigure your sources, or check the parser')
            return 
               
        query_id = self.store.find(Query.id, Query.source_id == source_id).one()
        if query_id is None:
            '''
                Add new query
            '''
            query = Query()
            query.source_id     = source_id
            query.type          = data['output_type']
            query.checksum      = unicode(checksum)
            query.creation_time = unicode(data['update_time'])
            self.store.add(query)
            self.store.flush()

            #self.qglogger.debug(len(data.keys()))
            if len(data.keys()) >= 4:
                filters = Filter()
                filters.query_id = query.id
                if protocol_version:
                    filters.protocol_version = unicode(protocol_version)
                if protocol:
                    filters.protocol = unicode(protocol)
                if tos:
                    filters.tos = tos
                if packets:
                    filters.packets = packets
                if bytes_:
                    filters.bytes = bytes_
                self.store.add(filters)
                self.store.flush()
                self.qglogger.debug('Query filters added to database.')

                # Now add output
                if query.type == 1:                           # means output gives only ip information
                    self.insertIPQuery(query.id, data['output'])
                elif query.type == 2:                         # means output gives only port information
                    self.insertPortQuery(query.id, data['output'])
                elif query.type == 3:                         # means output gives only ip-port information
                    self.insertIPPortQuery(query.id, data['output'])
                self.qglogger.debug('New query is added')
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
                if query.type != data['output_type']:
                    self.qglogger.error('Source output_type is changed')
                    self.qglogger.error('Query can not be updated!')
                    self.store.rollback()
                    return
                query.type = data['output_type']
                query.checksum = unicode(checksum)
                query.update_time = unicode(data['update_time'])

                self.qglogger.debug(len(data.keys()))
                if len(data.keys()) >= 4:
                    self.qglogger.debug('Q1')
                    try:
                        filters = self.store.find(Filter, Filter.query_id == query.id).one()
                        print type(filters)
                        print dir(filters)
                        print filters.id
                        if not filters:
                            filters = Filter()
                            filters.query_id = query.id
                        self.qglogger.debug('Query filters updated1')
                        filters.protocol_version = unicode(protocol_version)
                        filters.protocol = unicode(protocol)
                        filters.tos = tos
                        filters.packets = packets
                        self.qglogger.debug('Que1')
                        filters.bytes = bytes_
                        self.store.add(filters)
                        self.store.flush()
                        self.qglogger.debug('Query filters updated2')
                    except Exception, e:
                        self.qglogger.warning('got exception: %s, %s' % (e.args, e.message))
                        self.store.rollback()
                        return

                # Now add output
                if query.type == 1:                           # means output gives only ip information
                    self.insertIPQuery(query.id, data['output'])
                elif query.type == 2:                         # means output gives only port information
                    self.insertPortQuery(query.id, data['output'])
                elif query.type == 3:                         # means output gives only ip-port information
                    self.insertIPPortQuery(query.id, data['output'])
                self.qglogger.debug('Query is updated')
            elif checksum is None:
                ''' 
                   Fatal Error
                '''
                self.qglogger.error('Fatal Error : checksum is None')
                return
        self.store.commit()

        
    def insertIPQuery(self, query_id, ip_list):
        '''
            Insert ip query to database.
        '''
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        qid = query_id
        for ip in ip_list.split(' '):
            # Calculate the decimal type of ip and check if we already have it
            if ip is not ' ' and ip is not '':
                ip_int = dottedQuadToNum(ip)
                # Check if we already have this ip.
                ip_id = self.store.find(IP.id, IP.ip_int == ip_int).one()
                if ip_id is None:
                    try:
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
                        self.qglogger.debug('New query-ip relation is added')
                    except Exception, e:
                        self.qglogger.warning('got exception: %s, %s' % (e.args, e.message))
                        self.store.rollback()
                        return
                else:
                    self.qglogger.debug('We already have this ip')
                    # Check if we already have this ip-query relation
                    qp_id = self.store.find(QueryIP.id, (QueryIP.query_id == qid) & (QueryIP.ip_id == ip_id)).one()
                    if qp_id:
                        self.qglogger.debug('We already have this query-ip relation')
                    else:
                        try:
                            # Create query-ip relation
                            relation = QueryIP()
                            relation.query_id = qid
                            relation.ip_id = ip_id
                            self.store.add(relation)
                            self.qglogger.debug('New query-ip relation is added')
                        except Exception, e:
                            self.qglogger.warning('got exception: %s, %s' % (e.args, e.message))
                            self.store.rollback()
                            return


    def insertPortQuery(self, query_id, port_list):
        '''
            Insert port query to database.
        '''
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        qid = query_id
        for port in port_list.split(' '):
            # Check if port consists of digits
            if port.isdigit():
                # Check if we already have this port.
                port_id = self.store.find(Port.id, Port.port == int(port)).one()
                if port_id is None:
                    try:
                        # Insert new port and query-port relation.
                        port_obj = Port()
                        print port
                        port_obj.port = int(port)
                        self.store.add(port_obj)
                        self.store.flush()
                        self.qglogger.debug('New port is added')
                        relation = QueryPort()
                        relation.query_id = qid
                        relation.port_id = port_obj.id
                        self.store.add(relation)
                        self.store.flush()
                        self.qglogger.debug('New query-port relation is added')
                    except Exception, e:
                        self.qglogger.warning('got exception: %s, %s' % (e.args, e.message))
                        self.store.rollback()
                        return
                else:
                    self.qglogger.debug('We already have this port')
                    # Check if we already have this port-query relation
                    qp_id = self.store.find(QueryPort.id, (QueryPort.query_id == qid) & (QueryPort.port_id == port_id))
                    if qp_id is not None:
                        self.qglogger.debug('We already have this query-port relation')
                    else:
                        try:
                            # Create query-port relation
                            relation = QueryPort()
                            relation.query_id = qid
                            relation.port_id = port_id
                            self.qglogger.debug('New query-port relation is added')
                            self.store.add(relation)
                        except Exception, e:
                            self.qglogger.warning('got exception: %s, %s' % (e.args, e.message))
                            self.store.rollback()
                            return


    def validateIPPort(self, ip_port):
        '''
            Validate the ip:port output 
            Determine the format
            if output is correct,
                returns format and seperated form of ip, port
            else
                none
        '''
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        # Validate ip and port
        if ip_port == '':
            return

        print ip_port
        # Determine it's two sided output or not
        seperator = '-'

        if seperator in ip_port:
            self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
            format_ = 2
            # means output is in format2
            left = ip_port.split(seperator)[0]
            right = ip_port.split(seperator)[1]
            ip1, port1 = left.split(':')
            ip2, port2 = right.split(':')

            # validate for ip and port syntax
            if (
                 (is_valid_ipv4_address(ip1) or is_valid_ipv6_address(ip1)) and port1.isdigit()) and (
                 (is_valid_ipv4_address(ip2) or is_valid_ipv6_address(ip2)) and port2.isdigit()
               ):
                return [format_, ip1, port1, ip2, port2]
            else:
                self.qglogger.warning('Output is not valid')
                self.qglogger.warning(ip_port)
                return
        else:
            self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
            format_ = 1
            ip1, port1 = ip_port.split(':')
            if ( (is_valid_ipv4_address(ip1) or is_valid_ipv6_address(ip1)) and port1.isdigit()):
                return [format_, ip1, port1]
            else:
                self.qglogger.warning('Output is not valid')
                self.qglogger.warning(ip_port)
                return


    def insertIPPortQuery(self, query_id, ip_port_list):
        '''
            Insert ip-port query to database.
            example '193.140.11.11:11-192.168.7.5:123' --> (format1)
            example '193.140.14.71:45'                 --> (format2)
        '''
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        qid = query_id
        for ip_port in ip_port_list.split(' '):

            result = self.validateIPPort(ip_port)
            print result
            if not result:
                continue
            elif len(result)<3:
                format_ = result[0]
                print format_
                #ip = result[1]
                #port = result[2]
            elif len(result)>3:
                format_ = result[0]
                print format_
            
            # Check if we already have this ip-port entry.
            ip_port_id = self.store.find(IPPort.id, IPPort.ip_port == unicode(ip_port)).one()
            if ip_port_id is None:
                try:
                    # Insert new ip-port and query-ip-port relation.
                    ip_port_obj = IPPort()
                    #print ip_port
                    ip_port_obj.ip_port = unicode(ip_port)
                    ip_port_obj.format = format_
                    self.store.add(ip_port_obj)
                    self.store.flush()
                    self.qglogger.debug('New ip-port entry is added')
                    relation = QueryIPPort()
                    relation.query_id = qid
                    relation.ip_port_id = ip_port_obj.id
                    self.store.add(relation)
                    self.store.commit()
                    self.qglogger.debug('New query-ip-port relation is added')
                except Exception, e:
                    self.qglogger.warning('got exception: %s, %s' % (e.args, e.message))
                    self.store.rollback()
                    return
            else:
                self.qglogger.debug('We already have this ip-port')
                # Check if we already have this ip-port-query relation
                qip_id = self.store.find(QueryIPPort.id, (QueryIPPort.query_id == qid) & (QueryIPPort.ip_port_id == ip_port_id))
                if qip_id is not None:
                    self.qglogger.debug('We already have this query-ip-port relation')
                else:
                    try:
                        # Create query-ip-port relation
                        relation = QueryIPPort()
                        relation.query_id = qid
                        relation.ip_port_id = ip_port_id
                        self.qglogger.debug('New query-ip-port relation is added')
                        self.store.add(relation)
                        self.store.commit()
                    except Exception, e:
                        self.qglogger.warning('got exception: %s, %s' % (e.args, e.message))
                        self.store.rollback()
                        return
                

    def createQueryFilterExpressions(self, query_list=None):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        # 1) Fetch all queries,
        # 2) Check what kind of fields the query have, which will be used as netflow filter arguments : 
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
        
        ## ALL ## query_list = self.store.find(Query)
        ## ALL ## if not query_list.is_empty():
        ## ALL ##     for query in query_list:
        #        '''
        #            'checksum', 'creation_time', 'query_id', 'query_type', 'source', 'source_id', 'update_time'
        #        '''

        expr_dict = {}
        for query in query_list:
            # Create NfSen Query Filter Expressions
            if query.type == 1:
                expr = ''
                # we've only ip information
                ip_id_list = self.store.find(QueryIP.ip_id, QueryIP.query_id == query.id)
                if not ip_id_list.is_empty():
                    ip_list = self.store.find(IP.ip, In(IP.id, list(ip_id_list)))
                    for i in range(ip_list.count()):
                        expr +=  ' host ' + ip_list[i]
                        if i+1 < ip_list.count():
                                expr += ' or '
                    expr_dict[str(query.id)] = expr
                    #self.qglogger.debug('Returning IP list expression')
                else:
                    self.qglogger.warning('IP list is empty for this query, PROBLEM!')

            elif query.type == 2:
                expr = ''
                # we've only port information
                port_id_list = self.store.find(QueryPort.port_id, QueryPort.query_id == query.id)
                if not port_id_list.is_empty():
                    port_list = self.store.find(Port.port, In(Port.id, list(port_id_list)))
                    for i in range(port_list.count()):
                        expr +=  ' port ' + port_list[i]
                        if i+1 < port_list.count():
                                expr += ' or ' 
                    #self.qglogger.debug('Returning Port list expression')
                    expr_dict[str(query.id)] = expr
                else:
                    self.qglogger.warning('Port list is empty for this query, PROBLEM!')

            elif query.type == 3:

                # If FORMAT1
                    #Determine multidomain or not.
                    # if multidomain:
                        # Create ATTACKED DOMAIN query packet   
                        # Create ATTACKER DOMAIN query packet   
                        # Create MULTI DOMAIN query packet   
                    # if not multidomain but has an internal domain in one side:
                        # Create MALICIOUS DOMAIN query packet   
                        # Create MULTI DOMAIN query packet   
                    
                    #????#
                    # else 
                        # split both side of the output and turn into FORMAT2
                        # Create MULTI DOMAIN query packet for each part
                    #????#

                exprlist = []
                # we've ip-port tuple information
                ip_port_id_list = self.store.find(QueryIPPort.ip_port_id, QueryIPPort.query_id == query.id)
                if not ip_port_id_list.is_empty():
                    ip_port_list = self.store.find(IPPort, In(IPPort.id, list(ip_port_id_list)))
                    for i in range(ip_port_list.count()):
                        if ip_port_list[i].format_ == 1:
                            pass
                        elif ip_port_list[i].format_ == 2:
                            part1, part2 = ip_port_list[i].ip_port.split('-')
                            ip1, port1 = part1(':')
                            ip2, port2 = part2(':')
                            # We got tuples of both sides, now create expressions

                            # We assume that ip2 and port2 belongs to ATTACKED DOMAIN.

                            validation_expr1 = ' src ip ' + ip1 + ' src port ' + port1 + ' and ' + 'dst ip ' + ip2 + ' dst port ' + port2 + filters

                            master_expr1 = ' src ip ' + ip1 + ' src port any and ' + 'dst ip any dst port ' + port2 + filters

                            other_exprs = 'src ip ' + ip1 + ' src port any' + filters 
                                          'dst ip ' + ip1 + ' dst port any' + filters
                                          'additional filters permutations '


                            exprlist.append(' src ip ' + ip + ' src port ' + port)
                    #self.qglogger.debug('Returning IPPort list expression')
                    expr_dict[str(query.id)] = exprlist



                else:
                    self.qglogger.warning('IPPort list is empty for this query, PROBLEM!')

            #elif query.type == 4:
            #    domain_id_list = self.store.find(QueryDomain.domain_id, QueryDomain.query_id == query.id)
            #    if not domain_id_list.is_empty():
            #        domain_list = self.store.find(Domain.domain, In(Domain.id, list(domain_id_list)))
        return expr_dict


    def createQueryFromStatistics(self):
        pass




