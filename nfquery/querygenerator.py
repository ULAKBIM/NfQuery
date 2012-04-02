#!/usr/local/bin/python

import simplejson as json
import logging
import sys
import os.path
import hashlib
import subprocess
import datetime
from datetime import datetime

# nfquery imports
import db
import logger
import models
from models import *
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
 

    def generateQuery(self, parser=None):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        if parser:
            for index in range(len(self.sources)):
                if parser == self.sources[index].parser:
                    self.qglogger.debug('generating query for source : %s' % self.sources[index].source_name)
                    self.createQuery(self.sources[index].output_file)
                    return
        else:
            for index in range(len(self.sources)):
                self.qglogger.debug('generating query for source : %s' % self.sources[index].source_name)
                self.createQuery(self.sources[index].output_file)
                    

    def createQuery(self, output_file):
        '''
            Check parser output and create query for each expression.
        '''
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        output_fields = [ 'source_name', 'date', 'mandatory_fields', 'expr_list' ] 
        nfsen_filters = [ 'src_ip', 'src_port', 'dst_ip', 'dst_port', 'proto', 'protocol_version',  'packets', 
                          'bytes', 'duration', 'flags', 'tos', 'pps', 'bps', 'bpp', 'AS', 'scale' ]
        
        # useful function to print errors in the same pattern.
        def printOutputError(field, info):
            self.qglogger.error('%s is not valid' % field)
            self.qglogger.error('Please check your parser output %s' % output_file)
            self.qglogger.error('Error details : %s' % info)
        data = ''
        try:
            parser_output = open(output_file, 'r')
            data = json.load(parser_output)
            parser_output.close()
        except Exception, e:
            printOutputError('parser output', str(e))

        for index in range(len(data)):
            if set(output_fields).issubset(set(data[index].keys())):
                self.qglogger.debug('Parser output has necessary fields.')
                source = self.store.find(Source, Source.name == unicode(data[index]['source_name'])).one()
                if not source:
                    printOutputError('source_name', data[index]['source_name'])
                    return
                elif set(data[index]['mandatory_fields']).issubset(set(nfsen_filters)):
                    self.qglogger.debug('source name is valid')
                    try:
                        date = datetime.strptime(data[index]['date'], '%Y-%m-%d %H:%M')
                        self.qglogger.debug('date is valid')
                    except Exception, e:
                        printOutputError('date', data[index]['date'])
                        return
                    for expr in data[index]['expr_list']:
                        self.qglogger.debug(expr.keys())
                        self.qglogger.debug(data[index]['mandatory_fields'])
                        if set(data[index]['mandatory_fields']).issubset(set(expr.keys())):
                            if set(expr.keys()).issubset(set(nfsen_filters)):
                                query_id = self.insertQuery(source.id, date, expr)
                                if query_id:
                                    self.deriveOtherQueries(query_id, mandatory_fields)
                            else:
                                # Don't break the loop, iterate to next expr
                                printOutputError('expression syntax', expr)
                                continue
                        else:
                            self.qglogger.error('expr filters must be in mandatory_fields list')
                            printOutputError('mandatory_fields', expr)
                            continue
                    #sys.exit()
                else:
                    printOutputError('mandatory_fields', data[index]['mandatory_fields'])
                    continue


    def insertQuery(self, source_id, date, expr):
        '''
           Inserts query to database. 
        '''
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        
        # get the hash of expr to check if the query is updated or not.
        md5hash = hashlib.md5()
        md5hash.update(str(expr) + str(source_id))
        checksum = md5hash.hexdigest()
        
        query = self.store.find(Query, (Query.source_id == source_id) & (Query.checksum == unicode(checksum))).one()
        
        if not query:
            '''
                Insert new query.
            '''
            try:
                query = Query()
                query.source_id = source_id
                query.checksum = unicode(checksum)
                time_id = self.store.find(models.Time.id, models.Time.time == date).one()
                if time_id:
                    query.creation_time_id = time_id
                    query.update_time_id = time_id
                    self.qglogger.debug('here1')
                else:
                    self.qglogger.debug('here2')
                    time = models.Time()
                    time.time = date
                    self.store.add(time)
                    self.store.flush()
                    self.qglogger.debug('here4')
                    self.qglogger.warning(time.id)
                    query.update_time_id = time.id
                    query.creation_time_id = time.id
                # it's validation query.
                query.category_id = 1       
                # We'll insert query.type_id after determining it below.
                # For now, insert default type value
                query.type_id = 1
                self.qglogger.debug('here5')
                # print query details
                self.store.add(query)
                self.store.flush()
                self.qglogger.debug('here6')
            except Exception, e:
                self.qglogger.error('Error details : ')
                self.qglogger.error(e)
                self.store.rollback()
                return
            self.qglogger.debug('Line ')


            '''
                Every filter table has its own index from 0 to 15.
                Query type is determined with existing tables of the query by generating
                an array.
                For example if a query has info in src_ip and dst_port tables,
                its type will be '0,3' in query table.
            '''

            def generateQueryType(query_type, _type):
                if not query_type:
                    return str(_type)
                else:
                    query_type += ',' + str(_type)
                    return query_type


            query_type = ''
            for filter in expr.keys():
                # src_ip
                if filter == 'src_ip':
                    # ipv6 support should be added!
                    self.qglogger.debug('Line ')
                    if is_valid_ipv4_address(expr['src_ip']):
                        query_type = generateQueryType(query_type, 0)
                        ip_int = dottedQuadToNum(expr['src_ip'])
                        try:
                            # Check if we already have this ip.
                            ip_id = self.store.find(IP.id, IP.ip_int == ip_int).one()
                            if ip_id is None:
                                ip = IP()
                                ip.ip = unicode(expr['src_ip'])
                                ip.ip_int = ip_int
                                self.store.add(ip)
                                self.store.flush()
                                srcIP = SrcIP()
                                srcIP.ip_id = ip.id
                                srcIP.query_id = query.id
                                self.store.add(srcIP)
                                self.store.flush()
                                self.qglogger.debug('New src_ip is inserted')
                            else:
                                srcIP = SrcIP()
                                srcIP.ip_id = ip_id
                                srcIP.query_id = query.id
                                self.store.add(srcIP)
                                self.store.flush()
                        except Exception, e:
                            self.qglogger.error('Error details : ')
                            self.qglogger.error(e)
                            self.store.rollback()
                            return
                    else:
                        printOutputError('ip address', expr['src_ip'])
                        self.store.rollback()
                        return

                # src_port
                elif filter == 'src_port':
                    self.qglogger.debug('Line ')
                    if expr['src_port'].isdigit():
                        query_type = generateQueryType(query_type, 1)
                        # Check if we already have this port.
                        port_id = self.store.find(Port.id, Port.port == int(expr['src_port'])).one()
                        if port_id is None:
                            port = Port()
                            port.port = int(expr['src_port'])
                            self.store.add(port)
                            self.store.flush()
                            srcPort = SrcPort()
                            srcPort.query_id = query.id
                            srcPort.port_id = port.id
                            self.store.add(srcPort)
                            self.store.flush()
                            self.qglogger.debug('New src_port is inserted')
                        else:
                            srcPort = SrcPort()
                            srcPort.query_id = query.id
                            srcPort.port_id = port_id
                            self.store.add(srcPort)
                            self.store.flush()
                    else:
                        printOutputError('port', expr['src_port'])
                        self.store.rollback()
                        return

                #dst_ip
                elif filter == 'dst_ip':
                    self.qglogger.debug('Line ')
                    if is_valid_ipv4_address(expr['dst_ip']):
                        query_type = generateQueryType(query_type, 2)
                        ip_int = dottedQuadToNum(expr['dst_ip'])
                        # Check if we already have this ip.
                        ip_id = self.store.find(IP.id, IP.ip_int == ip_int).one()
                        if ip_id is None:
                            ip = IP()
                            ip.ip = unicode(expr['dst_ip'])
                            ip.ip_int = ip_int
                            self.store.add(ip)
                            self.store.flush()
                            dstIP = DstIP()
                            dstIP.ip_id = ip.id
                            dstIP.query_id = query.id
                            self.store.add(dstIP)
                            self.store.flush()
                            self.qglogger.debug('New dst_ip is inserted')
                        else:
                            dstIP = DstIP()
                            dstIP.ip_id = ip_id
                            dstIP.query_id = query.id
                            self.store.add(dstIP)
                            self.store.flush()
                    else:
                        printOutputError('ip address', expr['dst_ip'])
                        self.store.rollback()
                        return
               
                #dst_port
                elif filter == 'dst_port':
                    self.qglogger.debug('Line ')
                    if expr['dst_port'].isdigit():
                        query_type = generateQueryType(query_type, 3)
                        # Check if we already have this port.
                        port_id = self.store.find(Port.id, Port.port == int(expr['dst_port'])).one()
                        if port_id is None:
                            port = Port()
                            port.port = int(expr['dst_port'])
                            self.store.add(port)
                            self.store.flush()
                            dstPort = DstPort()
                            dstPort.query_id = query.id
                            dstPort.port_id = port.id
                            self.store.add(dstPort)
                            self.store.flush()
                            self.qglogger.debug('New dst_port is inserted')
                        else:
                            dstPort = DstPort()
                            dstPort.query_id = query.id
                            dstPort.port_id = port_id
                            self.store.add(dstPort)
                    else:
                        printOutputError('port', expr['dst_port'])
                        self.store.rollback()
                        return

                #proto
                elif filter == 'proto':
                    self.qglogger.debug('Line ')
                    if is_valid_proto(expr['proto']):
                        query_type = generateQueryType(query_type, 4)
                        proto = Proto()
                        proto.query_id = query.id
                        proto.proto = unicode(expr['proto'])
                        self.store.add(proto)
                    else:
                        printOutputError('proto', expr['proto'])
                        self.store.rollback()
                        return

                # protocol version
                elif filter == 'protocol_version':
                    self.qglogger.debug('Line ')
                    if is_valid_protocol_version(expr['protocol_version']):
                        query_type = generateQueryType(query_type, 5)
                        protocol_version = ProtocolVersion()
                        protocol_version.query_id = query.id
                        protocol_version.protocol_version = unicode(expr['protocol_version'])
                        self.store.add(proto)
                    else:
                        printOutputError('protocol_version', expr['protocol_version'])
                        self.store.rollback()
                        return

                # packets
                elif filter == 'packets':
                    self.qglogger.debug('Line ')
                    # range control should be done!
                    if expr['packets'].isdigit():
                        query_type = generateQueryType(query_type, 6)
                        packets = Packets()
                        packets.query_id = query.id
                        packets.packets = expr['packets']
                        self.store.add(packets)
                    else:
                        printOutputError('packets', expr['packets'])
                        self.store.rollback()
                        return

                # bytes
                elif filter == 'bytes':
                    self.qglogger.debug('Line ')
                    # range control should be done!
                    if expr['bytes'].isdigit():
                        query_type = generateQueryType(query_type, 7)
                        bytes = Bytes()
                        bytes.query_id = query.id
                        bytes.bytes = expr['bytes']
                        self.store.add(bytes)
                    else:
                        printOutputError('bytes', expr['bytes'])
                        self.store.rollback()
                        return

                # duration
                elif filter == 'duration':
                    self.qglogger.debug('Line ')
                    # range control should be done!
                    if expr['duration'].isdigit():
                        query_type = generateQueryType(query_type, 8)
                        duration = Duration()
                        duration.query_id = query.id
                        duration.duration = expr['duration']
                        self.store.add(duration)
                    else:
                        printOutputError('duration', expr['duration'])
                        self.store.rollback()
                        return

                #flags
                elif filter == 'flags':
                    self.qglogger.debug('Line ')
                    # range control should be done!
                    if is_valid_flags(expr['flags']):
                        query_type = generateQueryType(query_type, 9)
                        flags = Flags()
                        flags.query_id = query.id
                        flags.duration = expr['flags']
                        self.store.add(flags)
                    else:
                        printOutputError('flags', expr['flags'])
                        self.store.rollback()
                        return

                # tos
                elif filter == 'tos':
                    self.qglogger.debug('Line ')
                    # range control should be done!
                    if is_valid_tos(expr['tos']):
                        query_type = generateQueryType(query_type, 10)
                        tos = Tos()
                        tos.query_id = query.id
                        tos.tos = expr['tos']
                        self.store.add(tos)
                    else:
                        printOutputError('tos', expr['tos'])
                        self.store.rollback()
                        return

                # pps
                elif filter == 'pps':
                    self.qglogger.debug('Line ')
                    # range control should be done!
                    if expr['pps'].isdigit():
                        pps = PPS()
                        pps.query_id = query.id
                        query_type = generateQueryType(query_type, 11)
                        pps.pps = expr['pps']
                        self.store.add(pps)
                    else:
                        printOutputError('pps', expr['pps'])
                        self.store.rollback()
                        return

                # bps
                elif filter == 'bps':
                    self.qglogger.debug('Line ')
                    # range control should be done!
                    if expr['bps'].isdigit():
                        query_type = generateQueryType(query_type, 12)
                        bps = BPS()
                        bps.query_id = query.id
                        bps.bps = expr['bps']
                        self.store.add(bps)
                    else:
                        printOutputError('bps', expr['bps'])
                        self.store.rollback()
                        return

                # bpp
                elif filter == 'bpp':
                    self.qglogger.debug('Line ')
                    # range control should be done!
                    if expr['bpp'].isdigit():
                        query_type = generateQueryType(query_type, 13)
                        bpp = BPP()
                        bpp.query_id = query.id
                        bpp.bpp = expr['bpp']
                        self.store.add(bpp)
                    else:
                        printOutputError('bpp', expr['bpp'])
                        self.store.rollback()
                        return

                # AS
                elif filter == 'AS':
                    self.qglogger.debug('Line ')
                    # range control should be done!
                    if expr['AS'].isdigit():
                        query_type = generateQueryType(query_type, 14)
                        asn = ASN()
                        asn.query_id = query.id
                        asn.asn = expr['AS']
                        self.store.add(asn)
                    else:
                        printOutputError('AS', expr['AS'])
                        self.store.rollback()
                        return

                # scale
                elif filter == 'scale':
                    self.qglogger.debug('Line ')
                    # range control should be done!
                    if is_valid_scale(expr['scale']):
                        query_type = generateQueryType(query_type, 15)
                        flags = flags()
                        flags.query_id = query.id
                        flags.flags = expr['scale']
                        self.store.add()
                    else:
                        printOutputError('scale', expr['scale'])
                        self.store.rollback()
                        return

            # Now, insert query type.
            try:
                type_id = self.store.find(Type.id, Type.type == unicode(query_type)).one()
                if type_id:
                    query.type_id = type_id
                else:
                    type = Type()
                    type.type = unicode(query_type)
                    self.store.add(type)
                    self.store.flush()
                    query.type_id = type.id
            except Exception,e:
                self.qglogger.warning('ERROR')
                self.qglogger.warning(e)
                return
            self.qglogger.debug('New query is inserted succesfully')
        else:
            '''
                Update update_time of the query.
            '''
            self.qglogger.debug('Query exists in the database.')
            update_time_id = self.store.find(models.Time.id, models.Time.time == date).one()
            if update_time_id:
                query.update_time_id = update_time_id
            else:
                time = models.Time()
                time.time = date
                self.store.add(time)
                self.store.flush()
                query.update_time_id = time.id

        # end of insertQuery
        try:
            self.store.commit()
        except Exception, e:
            self.qglogger.error(e)
            self.store.rollback()
            return
        

    def createQueryFilterExpressions(self, query_list=None):
        '''
           Create NfSen Query Filter Expressions
        '''
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

        query_packet = {}
        for query in query_list:
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
                    query_packet[str(query.id)] = expr
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
                    query_packet[str(query.id)] = expr
                else:
                    self.qglogger.warning('Port list is empty for this query, PROBLEM!')

            elif query.type == 3:
                #if FORMAT1
                    #Determine multidomain or not.
                    # if multidomain:
                        # Create ATTACKED DOMAIN query packet   
                        # Create ATTACKER DOMAIN query packet   
                        # Create MULTI DOMAIN query packet   
                    # if not multidomain but has an internal domain in one side:
                        # Create MALICIOUS DOMAIN query packet   
                        # Create MULTI DOMAIN query packet
                #????#
                #else 
                    # split both side of the output and turn into FORMAT2
                    # Create MULTI DOMAIN query packet for each part
                #????#
                exprlist = []
                # we've ip-port tuple information
                ip_port_id_list = self.store.find(QueryIPPort.ip_port_id, QueryIPPort.query_id == query.id)
                if not ip_port_id_list.is_empty():
                    ip_port_list = self.store.find(IPPort, In(IPPort.id, list(ip_port_id_list)))
                    for i in range(ip_port_list.count()):
                        #print dir(ip_port_list[i])
                        #print ip_port_list[i].format_
                        #print ip_port_list[i].ip_port

                        if ip_port_list[i].format_ == 1:
                            pass
                        elif ip_port_list[i].format_ == 2:
                            part1, part2 = ip_port_list[i].ip_port.split('-')
                            ip1, port1 = part1.split(':')
                            ip2, port2 = part2.split(':')

                            # We assume that ip2:port2 belongs to ATTACKED DOMAIN.
                            v1 = '( src ip ' + ip1 + ' src port ' + port1 + ' and ' + 'dst ip ' + ip2 + ' dst port ' + port2 + ' )' 
                            v2 = '( src ip ' + ip2 + ' src port ' + port2 + ' and ' + 'dst ip ' + ip1 + ' dst port ' + port1 + ' )'
                            validation_query = v1 + ' or ' + v2
                            print 'validation_query:', validation_query
                            
                            m1 = '( src ip ' + ip1 + ' src port any and ' + 'dst ip any dst port ' + port2 + ' )'
                            m2 = '( src ip ' + ip2 + ' src port any and ' + 'dst ip any dst port ' + port1 + ' )'
                            master_query = m1 + ' or ' + m2
                            print 'master_query:', master_query
                            print '\n'
                            #add_exprs = 'src ip ' + ip1 + ' src port any' + filters 
                            #              'dst ip ' + ip1 + ' dst port any' + filters
                            #              'additional filters permutations '
                            exprlist.append(validation_query)
                            exprlist.append(master_query)

                    #self.qglogger.debug('Returning IPPort list expression')
                    query_packet[str(query.id)] = exprlist
                else:
                    self.qglogger.warning('IPPort list is empty for this query, PROBLEM!')

            #elif query.type == 4:
            #    domain_id_list = self.store.find(QueryDomain.domain_id, QueryDomain.query_id == query.id)
            #    if not domain_id_list.is_empty():
            #        domain_list = self.store.find(Domain.domain, In(Domain.id, list(domain_id_list)))
        return query_packet


    def createQueryFromStatistics(self):
        pass




