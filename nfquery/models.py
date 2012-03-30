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
    registered = Bool()
 
    prefix = Reference(prefix_id, Prefix.id) 


class Parser(object):
   
    __storm_table__ = 'parser'

    id = Int(primary=True)
    name = Unicode()
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

    threat = Reference(threat_id, Threat.id)
    parser =  Reference(parser_id, Parser.id)


class Query(object):
    
    __storm_table__ = 'query'
    
    id = Int(primary=True)
    source_id = Int()
    update_time = Unicode()
    type = Int()
    checksum = Unicode()
    creation_time = Unicode()

    source =  Reference(source_id, Source.id)


class Subscription(object):
    
    __storm_table__ = 'subscription'
    
    id = Int(primary=True)
    type = Int()
    name = Unicode()
    timeout = DateTime()


class SubscriptionPackets(object):
    
    __storm_table__ = 'subscription_packets'
    
    id = Int(primary=True)
    subscription_id = Int()
    query_id = Int()
    tags = Unicode()

    subscription = Reference(subscription_id, Subscription.id)
    query = Reference(query_id, Query.id)


class Statistics(object):

    __storm_table__ = 'statistics'

    id = Int(primary=True)
    query_id = Int()

    query = Reference(query_id, Query.id)


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
    proto = Unicode()
    
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
    
    __storm_table__ = ''
  
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

