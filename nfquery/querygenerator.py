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
        
        # BUNU KALDIR
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
                        #self.qglogger.debug(expr.keys())
                        #self.qglogger.debug(data[index]['mandatory_fields'])
                        if set(data[index]['mandatory_fields']).issubset(set(expr.keys())):
                            if set(expr.keys()).issubset(set(nfsen_filters)):
                                self.insertQuery(source.id, date, expr)
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

    # query type generation util
    def generateQueryType(self, type_):
        # self.query_type = self.query_type + '%s' if self.query_type else ','
        if not self.query_type:
            self.query_type = str(type_)
        else:
            self.query_type += ',' + str(type_)


    def insertQuery(self, source_id, date, expr):
        '''
           Insert/Update query.
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
                # For now, set it to default type value 1.
                query.type_id = 1
                self.qglogger.debug('here5')
                # print query details
                self.store.add(query)
                self.store.flush()
                self.qglogger.debug('here6')
            except Exception, e:
                self.qglogger.warning(e)
                return
            '''
                Every filter table has its own index from 0 to 15.
                Query type is determined by generating an array with existing fields of the query.
                For example if a query has info in src_ip and dst_port tables,
                its type will be '0,3' in query table.
            '''
            self.query_type = ''
            for filter in expr.keys():
                try:
                    # src_ip
                    if filter == 'src_ip':
                        self.insertSrcIP(expr['src_ip'], query.id)
                    # src_port
                    elif filter == 'src_port':
                        self.insertSrcPort(expr['src_port'], query.id)
                    #dst_ip
                    elif filter == 'dst_ip':
                        self.insertDstIP(expr['dst_ip'], query.id)
                    # dst_port
                    elif filter == 'dst_port':
                        self.insertDstPort(expr['dst_port'], query.id)
                    #proto
                    elif filter == 'proto':
                        self.insertProto(expr['proto'], query.id)
                    # protocol version
                    elif filter == 'protocol_version':
                        self.insertProtocolVersion(expr['protocol_version'], query.id)
                    # packets
                    elif filter == 'packets':
                        self.insertPackets(expr['packets'], query.id)
                    # bytes
                    elif filter == 'bytes':
                        self.insertBytes(expr['bytes'], query.id)
                    # duration
                    elif filter == 'duration':
                        self.insertDuration(expr['duration'], query.id)
                    #flags
                    elif filter == 'flags':
                        self.insertFlags(expr['flags'], query.id)
                    # tos
                    elif filter == 'tos':
                        self.insertTOS(expr['tos'], query.id)
                    # pps
                    elif filter == 'pps':
                        self.insertPPS(expr['pps'], query.id)
                    # bps
                    elif filter == 'bps':
                        self.insertBPS(expr['bps'], query.id)
                    # bpp
                    elif filter == 'bpp':
                        self.insertBPP(expr['bpp'], query.id)
                    # AS
                    elif filter == 'AS':
                        self.insertAS(expr['AS'], query.id)
                    # scale
                    elif filter == 'scale':
                        self.insertScale(expr['scale'], query.id)
                except Exception, e:
                    self.qglogger.warning(e)
                    return
            # Now, insert other query details.
            try:
                type_id = self.store.find(Type.id, Type.type == unicode(self.query_type)).one()
                if type_id:
                    query.type_id = type_id
                else:
                    type = Type()
                    type.type = unicode(self.query_type)
                    self.store.add(type)
                    self.store.flush()
                    query.type_id = type.id
                    self.store.commit()
                    self.qglogger.debug('New query is inserted succesfully')
            except Exception, e:
                self.qglogger.warning(e)
                return
        else:
            '''
                Update update_time of the query.
            '''
            self.qglogger.debug('Query exists in the database.')
            try:
                update_time_id = self.store.find(models.Time.id, models.Time.time == date).one()
                if update_time_id:
                    query.update_time_id = update_time_id
                else:
                    time = models.Time()
                    time.time = date
                    self.store.add(time)
                    self.store.flush()
                    query.update_time_id = time.id
                    self.store.commit()
                    self.qglogger.debug('Query time is updated')
            except Exception, e:
                self.qglogger.warning(e)
                return


    def insertSrcIP(self, src_ip, query_id):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        # ipv6 support should be added!
        if is_valid_ipv4_address(src_ip):
            self.generateQueryType(0)
            ip_int = dottedQuadToNum(src_ip)
            ip_id = self.store.find(IP.id, IP.ip_int == ip_int).one()
            if not ip_id:
                ip = IP()
                ip.ip = unicode(src_ip)
                ip.ip_int = ip_int
                self.store.add(ip)
                self.store.flush()
                srcIP = SrcIP()
                srcIP.ip_id = ip.id
                srcIP.query_id = query_id
                self.store.add(srcIP)
                self.store.flush()
                self.qglogger.debug('New src_ip is inserted')
            else:
                srcIP = SrcIP()
                srcIP.ip_id = ip_id
                srcIP.query_id = query_id
                self.store.add(srcIP)
                self.store.flush()
        else:
            raise Exception, "src_ip is not valid"


    def insertSrcPort(self, src_port, query_id):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        if src_port.isdigit():
            self.generateQueryType(1)
            # Check if we already have this port.
            port_id = self.store.find(Port.id, Port.port == int(src_port)).one()
            if not port_id:
                port = Port()
                port.port = int(src_port)
                self.store.add(port)
                self.store.flush()
                srcPort = SrcPort()
                srcPort.query_id = query_id
                srcPort.port_id = port.id
                self.store.add(srcPort)
                self.store.flush()
                self.qglogger.debug('New src_port is inserted')
            else:
                srcPort = SrcPort()
                srcPort.query_id = query_id
                srcPort.port_id = port_id
                self.store.add(srcPort)
                self.store.flush()
        else:
            raise Exception, "src_port is not valid." 


    def insertDstIP(self, dst_ip, query_id):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        if is_valid_ipv4_address(dst_ip):
            self.generateQueryType(2)
            ip_int = dottedQuadToNum(dst_ip)
            ip_id = self.store.find(IP.id, IP.ip_int == ip_int).one()
            if not ip_id:
                ip = IP()
                ip.ip = unicode(dst_ip)
                ip.ip_int = ip_int
                self.store.add(ip)
                self.store.flush()
                dstIP = DstIP()
                dstIP.ip_id = ip.id
                dstIP.query_id = query_id
                self.store.add(dstIP)
                self.store.flush()
                self.qglogger.debug('New dst_ip is inserted')
            else:
                dstIP = DstIP()
                dstIP.ip_id = ip_id
                dstIP.query_id = query_id
                self.store.add(dstIP)
                self.store.flush()
        else:
            raise Exception, "dst_ip is not valid." 


    def insertDstPort(self, dst_port, query_id):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        if dst_port.isdigit():
            self.generateQueryType(1)
            port_id = self.store.find(Port.id, Port.port == int(dst_port)).one()
            if not port_id:
                port = Port()
                port.port = int(dst_port)
                self.store.add(port)
                self.store.flush()
                dstPort = DstPort()
                dstPort.query_id = query_id
                dstPort.port_id = port.id
                self.store.add(dstPort)
                self.store.flush()
                self.qglogger.debug('New dst_port is inserted')
            else:
                dstPort = DstPort()
                dstPort.query_id = query_id
                dstPort.port_id = port_id
                self.store.add(dstPort)
                self.store.flush()
        else:
            raise Exception, "dst_port is not valid." 


    def insertProto(self, proto_, query_id):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        if is_valid_proto(proto_):
            self.generateQueryType(4)
            proto = Proto()
            proto.query_id = query_id
            proto.proto = unicode(proto_)
            self.store.add(proto)
        else:
            raise Exception, 'proto is not valid.' 


    def insertProtocolVersion(self, protocol_version_, query_id):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        if is_valid_protocol_version(protocol_version_):
            self.generateQueryType(5)
            protocol_version_ = ProtocolVersion()
            protocol_version_.query_id = query_id
            protocol_version_.protocol_version = unicode(protocol_version_)
            self.store.add(protocol_version_)
        else:
            raise Exception, 'protocol_version is not valid.' 


    def insertPackets(self, packets_, query_id):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        # range control should be done!
        if packets_.isdigit():
            self.generateQueryType(6)
            packets = Packets()
            packets.query_id = query_id
            packets.packets = packets_
            self.store.add(packets)
        else:
            raise Exception, 'packets is not valid.' 
            
        
    def insertBytes(bytes_, query_id):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        # range control should be done!
        if bytes_.isdigit():
            self.generateQueryType(7)
            bytes = Bytes()
            bytes.query_id = query_id
            bytes.bytes = bytes_
            self.store.add(bytes)
        else:
            raise Exception, 'bytes is not valid.' 

            
    def insertDuration(self, duration_, query_id):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        # range control should be done!
        if duration_.isdigit():
            self.generateQueryType(8)
            duration = Duration()
            duration.query_id = query_id
            duration.duration = duration_
            self.store.add(duration)
        else:
            raise Exception, 'duration is not valid.' 


    def insertFlags(self, flags_, query_id):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        # range control should be done!
        if is_valid_flags(flags_):
            self.generateQueryType(9)
            flags = Flags()
            flags.query_id = query_id
            flags.duration = flags_
            self.store.add(flags)
        else:
            raise Exception, 'flags is not valid.' 
       

    def insertTOS(self, tos_, query_id): 
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        # range control should be done!
        if is_valid_tos(tos_):
            self.generateQueryType(10)
            tos = Tos()
            tos.query_id = query_id
            tos.tos = tos_
            self.store.add(tos)
        else:
            raise Exception, 'tos is not valid.' 


    def insertPPS(self, pps_, query_id):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        # range control should be done!
        if pps_.isdigit():
            pps = PPS()
            pps.query_id = query_id
            self.generateQueryType(11)
            pps.pps = pps_
            self.store.add(pps)
        else:
            raise Exception, 'pps is not valid.' 
        

    def insertBPS(self, bps_, query_id):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        # range control should be done!
        if bps_.isdigit():
            self.generateQueryType(12)
            bps = BPS()
            bps.query_id = query_id
            bps.bps = bps_
            self.store.add(bps)
        else:
            raise Exception, 'bps is not valid.' 


    def insertBPP(self, bpp_, query_id):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        # range control should be done!
        if bpp_.isdigit():
            self.generateQueryType(13)
            bpp = BPP()
            bpp.query_id = query_id
            bpp.bpp = bpp_
            self.store.add(bpp)
        else:
            raise Exception, 'bytes is not valid.' 


    def insertAS(self, AS_, query_id):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        # range control should be done!
        if AS_.isdigit():
            self.generateQueryType(14)
            asn = ASN()
            asn.query_id = query_id
            asn.asn = AS_
            self.store.add(asn)
        else:
            raise Exception, 'AS_ is not valid.' 
     

    def insertScale(self, scale_, query_id):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        # range control should be done!
        if is_valid_scale(scale_):
            self.generateQueryType(15)
            scale = Scale()
            scale.query_id = query_id
            scale.scale = scale_
            self.store.add(scale)
        else:
            raise Exception, 'scale is not valid.' 


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




