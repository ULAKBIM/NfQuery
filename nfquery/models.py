from storm.locals import *


class Domain(object):
    
    __storm_table__ = 'domain'

    id = Int(primary=True)
    name = Unicode()


class IP(object):

    __storm_table__ = 'ip'

    id = Int(primary=True)
    ip = Unicode()
    ip_int = Int()


class IPPort(object):
    
    __storm_table__ = 'ip_port'

    id = Int(primary=True)
    ip_port = Unicode()
    format_ = Int()


class Port(object):

    __storm_table__ = 'port'

    id = Int(primary=True)
    port = Int()


class Parser(object):
   
    __storm_table__ = 'parser'

    id = Int(primary=True)
    name = Unicode()
    time_interval = Int()


class List(object):

    __storm_table__ = 'list'
    
    id  = Int(primary=True)
    type = Unicode()


class Source(object):

    __storm_table__ = 'source'

    id = Int(primary=True)
    name = Unicode()
    link = Unicode()
    checksum = Unicode()
    list_id = Int()
    parser_id = Int()

    list_ = Reference(list_id, List.id)
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
    
    
class QueryDomain(object):
    
    __storm_table__ = 'query_domain'
   
    id = Int(primary=True)
    domain_id = Int() 
    query_id = Int() 

    query = Reference(query_id, Query.id)
    domain = Reference(domain_id, Domain.id)


class QueryPort(object):
    
    __storm_table__ = 'query_port'
   
    id = Int(primary=True)
    port_id = Int() 
    query_id = Int() 

    query = Reference(query_id, Query.id)
    port = Reference(port_id, Port.id)


class QueryIP(object):
    
    __storm_table__ = 'query_ip'
   
    id = Int(primary=True)
    ip_id = Int() 
    query_id = Int() 

    query = Reference(query_id, Query.id)
    ip = Reference(ip_id, IP.id)


class QueryIPPort(object):
    
    __storm_table__ = 'query_ip_port'
   
    id = Int(primary=True)
    ip_port_id = Int() 
    query_id = Int() 

    query = Reference(query_id, Query.id)
    ip_port = Reference(id, IPPort.id)


class Filter(object):

    __storm_table__ = 'filter'

    id = Int(primary=True)
    query_id = Int()
    protocol_version = Unicode()
    protocol = Unicode()
    tos = Int()
    packets = Int()
    bytes = Int()

    query = Reference(query_id, Query.id)


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



