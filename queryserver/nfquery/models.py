# This file is part of NfQuery.  NfQuery is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright NfQuery Team Members

from storm.locals import *


class Prefix(object):

    __storm_table__ = 'prefix'

    id = Int(primary=True)
    prefix = Unicode()


class Plugin(object):

    __storm_table__ = 'plugin'

    id = Int(primary=True)
    organization = Unicode()
    adm_name = Unicode()
    adm_mail = Unicode()
    adm_tel = Unicode()
    adm_publickey_file = Unicode()
    prefix_id = Int()
    plugin_ip = Unicode()
    checksum = Unicode()
    registered = Int()
 
    prefix = Reference(prefix_id, Prefix.id) 


class Parser(object):
   
    __storm_table__ = 'parser'

    id = Int(primary=True)
    name = Unicode()
    checksum = Unicode()
    time_interval = Int()


class Threat(object):

    __storm_table__ = 'threat'
    
    id  = Int(primary=True)
    type = Unicode()


class Source(object):

    __storm_table__ = 'source'

    id = Int(primary=True)
    name = Unicode()
    link = Unicode()
    checksum = Unicode()
    threat_id = Int()
    parser_id = Int()
    is_active = Int()
    threat = Reference(threat_id, Threat.id)
    parser =  Reference(parser_id, Parser.id)


class Category(object):

    __storm_table__ = 'category'

    id = Int(primary=True)
    category = Unicode()


class Time(object):

    __storm_table__ = 'time'

    id = Int(primary=True)
    time = DateTime()


class Type(object):

    __storm_table__ = 'type'

    id = Int(primary=True)
    type = Unicode()


class Query(object):
    
    __storm_table__ = 'query'
    
    id = Int(primary=True)
    type_id = Int()
    source_id = Int()
    checksum = Unicode()
    creation_time_id = Int()
    update_time_id = Int()
    category_id = Int()
    filter_cache = Unicode()

    source =  Reference(source_id, Source.id)
    type =  Reference(type_id, Type.id)
    creation_time = Reference(creation_time_id, Time.id)
    update_time = Reference(update_time_id, Time.id)
    category = Reference(category_id, Category.id)


class QueryPacket(object):
    
    __storm_table__ = 'query_packet'

    id = Int(primary=True)
    validation_id = Int()
    query_id = Int()

    validation = Reference(validation_id, Query.id)
    query = Reference(query_id, Query.id)


class Subscription(object):
    
    __storm_table__ = 'subscription'
    
    id = Int(primary=True)
    type = Int()
    name = Unicode()


class SubscriptionPacket(object):
    
    __storm_table__ = 'subscription_packet'
    
    id = Int(primary=True)
    subscription_id = Int()
    query_packet_id = Int()
    tags = Unicode()

    subscription = Reference(subscription_id, Subscription.id)
    query_packet = Reference(query_packet_id, QueryPacket.id)




class IP(object):

    __storm_table__ = 'ip'

    id = Int(primary=True)
    ip = Unicode()
    ip_int = Int()


class Port(object):

    __storm_table__ = 'port'

    id = Int(primary=True)
    port = Int()


class SrcIP(object):

    __storm_table__ = 'src_ip'

    id = Int(primary=True)
    ip_id = Int()
    query_id = Int()

    query = Reference(query_id, Query.id)
    ip = Reference(ip_id, IP.id)

 
class DstIP(object):

    __storm_table__ = 'dst_ip'

    id = Int(primary=True)
    ip_id = Int()
    query_id = Int()

    query = Reference(query_id, Query.id)
    ip = Reference(ip_id, IP.id)

    
class SrcPort(object):
    
    __storm_table__ = 'src_port'
   
    id = Int(primary=True)
    port_id = Int() 
    query_id = Int() 

    query = Reference(query_id, Query.id)
    port = Reference(port_id, Port.id)


class DstPort(object):
    
    __storm_table__ = 'dst_port'
   
    id = Int(primary=True)
    port_id = Int() 
    query_id = Int() 

    query = Reference(query_id, Query.id)
    port = Reference(port_id, Port.id)


class Proto(object):
    
    __storm_table__ = 'proto'
  
    id = Int(primary=True)
    query_id = Int()
    proto = Unicode()
    
    query = Reference(query_id, Query.id)


class ProtocolVersion(object):
    
    __storm_table__ = 'protocol_version'
  
    id = Int(primary=True)
    query_id = Int()
    protocol_version = Unicode()
    
    query = Reference(query_id, Query.id)


class Packets(object):
    
    __storm_table__ = 'packets'
  
    id = Int(primary=True)
    query_id = Int()
    packets = Int()

    query = Reference(query_id, Query.id)


class Bytes(object):
    
    __storm_table__ = 'bytes'
  
    id = Int(primary=True)
    query_id = Int()
    bytes = Int()
    
    query = Reference(query_id, Query.id)



class Duration(object):
    
    __storm_table__ = 'duration'
  
    id = Int(primary=True)
    query_id = Int()
    duration = Int()

    query = Reference(query_id, Query.id)


class Flags(object):
    
    __storm_table__ = 'flags'
  
    id = Int(primary=True)
    query_id = Int()
    flags = Unicode()
    
    query = Reference(query_id, Query.id)


class Tos(object):
    
    __storm_table__ = 'tos'
  
    id = Int(primary=True)
    query_id = Int()
    tos = Int()
    
    query = Reference(query_id, Query.id)


class PPS(object):
    
    __storm_table__ = 'pps'
  
    id = Int(primary=True)
    query_id = Int()
    pps = Int()
    
    query = Reference(query_id, Query.id)


class BPS(object):
    
    __storm_table__ = 'bps'
  
    id = Int(primary=True)
    query_id = Int()
    bps = Int()
    
    query = Reference(query_id, Query.id)


class BPP(object):
    
    __storm_table__ = 'bpp'
  
    id = Int(primary=True)
    query_id = Int()
    bpp = Int()
    
    query = Reference(query_id, Query.id)


class ASN(object):
    
    __storm_table__ = 'ASN'
  
    id = Int(primary=True)
    query_id = Int()
    asn = Unicode()
    
    query = Reference(query_id, Query.id)

class Scale(object):
    
    __storm_table__ = 'scale'
  
    id = Int(primary=True)
    query_id = Int()
    scale = Unicode()

    query = Reference(query_id, Query.id)

class Alert(object):

    __storm_table__ = 'alert'
  
    id = Int(primary=True)
    #alert_id = Int()
    alert_type = Int()
    query_id = Int()
    identified_plugin_id = Int()
    identifier_plugin_id = Int()
   # start_time_id = Int()
   # end_time_id = Int()
    start_time = Int()
    end_time = Int()
    first_seen = Int()
    checksum = Unicode()
    #plugin_id = Int()

    query = Reference(query_id, Query.id)
#    plugin = Reference(plugin_id, Plugin.id)
    identified_plugin = Reference(identified_plugin_id, Plugin.id)
    identifier_plugin = Reference(identifier_plugin_id, Plugin.id)
   # start_time = Reference(start_time_id, Time.id)
   # end_time = Reference(end_time_id, Time.id)


class Statistics(object):

    __storm_table__ = 'statistics'

    id = Int(primary=True)
    alert_id = Int()
    number_of_flows = Int()
    number_of_bytes = Int()
    number_of_packets = Int()
#    start_time = Int()
#    end_time = Int()

    alert = Reference(alert_id, Alert.id)
    #start_time = Reference(start_time_id, Time.id)
    #end_time = Reference(end_time_id, Time.id)
