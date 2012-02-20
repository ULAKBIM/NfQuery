from storm.locals import *


class Query(object):
    
    __storm_table__ = 'query'
    
    query_id = Int(primary=True)
    source_id = Int()
    update_time = Unicode()
    query_type = Int()
    hash_value = Unicode()
    creation_time = Unicode()
    # we 'll go on


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
 
    prefix = Reference(prefix_id, PrefixList.prefix_id) 


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
    source_checksum = Unicode()
    #source_checksum = RawStr()
    list_id = Int()
    parser_id = Int()

    list_ = Reference(list_id, List.list_id)
    parser =  Reference(parser_id, Parser.parser_id)



