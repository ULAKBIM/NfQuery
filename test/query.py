#!/usr/local/bin/python

class Query():
    '''
        Query class for storing etracted information from sources
        
        1) Define a JSON schema for the query data structure
        
        queryid        : Index of the query 
        ip             : Aggregated ip list of the selected blocklist source
        domain         : Aggregated domainlist of the selected blocklist source
        port           : Port Information 
        source_name    : Selected security source name for exm : amada.ch or spyeyetracker
        threat_type    : Type of the threat such as Botnet, SPAM, DNS Blocklist etc.
        threat_desc    : Name of the threat such as FAKE-AV, Spyeye, Zeus, AmadaBlocklist etc.
        creation_time  : Creation time of this query that will be used when checking
                         if there is an update for the created query

    '''

    def __init__(self, queryid, source_name, threat_type, creation_time, 
                 ip=None, domain=None, port=None):
        self.queryid = queryid
        if (ip is None) and (domain is None):
            sys.exit("both ip and domain can not be EMPTY or None at the same time\nyou have to set at least one of them\n")
        else:
            self.ip = ip
            self.domain = domain
        self.port = port
        self.source_name = source_name
        self.threat_type = threat_type
        self.threat_name = threat_name 
        self.creation_time = creation_time

