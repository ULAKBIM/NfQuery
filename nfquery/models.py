from storm.locals import *


class Domain(object):
    
    __storm_table__ = 'domain'

    domain_id = Int(primary=True)
    domain_name = Unicode()


class IP(object):

    __storm_table__ = 'ip'

    ip_id = Int(primary=True)
    ip = Unicode()
    ip_int = Int()


class Port(object):

    __storm_table__ = 'port'

    port_id = Int(primary=True)
    port = Int()


class Parser(object):
   
    __storm_table__ = 'parser'

    parser_id = Int(primary=True)
    parser_script = Unicode()
    time_interval = Int()


class List(object):

    __storm_table__ = 'list'
    
    list_id  = Int(primary=True)
    list_type = Unicode()


class Source(object):

    __storm_table__ = 'source'

    source_id = Int(primary=True)
    source_name = Unicode()
    source_link = Unicode()
    checksum = Unicode()
    list_id = Int()
    parser_id = Int()

    list_ = Reference(list_id, List.list_id)
    parser =  Reference(parser_id, Parser.parser_id)


class Query(object):
    
    __storm_table__ = 'query'
    
    query_id = Int(primary=True)
    source_id = Int()
    update_time = Unicode()
    query_type = Int()
    checksum = Unicode()
    creation_time = Unicode()

    source =  Reference(source_id, Source.source_id)


class Subscription(object):
    
    __storm_table__ = 'subscription'
    
    subscription_id = Int(primary=True)
    subscription_type = Int()
    subscription_name = Unicode()
    timeout = DateTime()


class SubscriptionPackets(object):
    
    __storm_table__ = 'subscription_packets'
    
    subs_packet_id = Int(primary=True)
    subscription_id = Int()
    query_id = Int()
    tags = Unicode()

    subscription = Reference(subscription_id, Subscription.subscription_id)
    query = Reference(query_id, Query.query_id)
    
    
class QueryDomain(object):
    
    __storm_table__ = 'query_domain'
   
    qd_id = Int(primary=True)
    domain_id = Int() 
    query_id = Int() 

    query = Reference(query_id, Query.query_id)
    domain = Reference(domain_id, Domain.domain_id)


class QueryPort(object):
    
    __storm_table__ = 'query_port'
   
    qpo_id = Int(primary=True)
    port_id = Int() 
    query_id = Int() 

    query = Reference(query_id, Query.query_id)
    port = Reference(port_id, Port.port_id)


class QueryIP(object):
    
    __storm_table__ = 'query_ip'
   
    qp_id = Int(primary=True)
    ip_id = Int() 
    query_id = Int() 

    query = Reference(query_id, Query.query_id)
    ip = Reference(ip_id, IP.ip_id)


class PrefixList(object):

    __storm_table__ = 'prefix_list'

    prefix_id = Int(primary=True)
    prefix = Unicode()


class Plugin(object):

    __storm_table__ = 'plugin'

    plugin_id = Int(primary=True)
    organization = Unicode()
    adm_name = Unicode()
    adm_mail = Unicode()
    adm_tel = Unicode()
    adm_publickey_file = Unicode()
    prefix_id = Int()
    plugin_ip = Unicode()
    checksum = Unicode()
    registered = Bool()
 
    prefix = Reference(prefix_id, PrefixList.prefix_id) 



