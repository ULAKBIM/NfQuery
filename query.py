#!/usr/local/bin/python

import sys

class query():
    '''
        Query class for storing etracted information from sources.
        
        source_name          : Name of the security source
                               example source_name : "Amada"
                               example source_name : "DFN-NREN"
                               example source_name : "ULAKBIM-NREN"

        source_desc          : Descrioption of the security source name
                               example source_name : "Amada C&C IP Blocklist"
                               example source_desc : "DFN NREN Honeypot"
                               example source_desc : "ULAKBIM NREN Blacklist"

        source_link          : Download link of the security source
                               example source_link : "http://amada.abuse.ch/blocklist.php?download=ipblocklist" 

        threat_type          : Type of the given threat information. Threat type must be one of the 
                               threat types which are published in nfquery website. Malware, Botnet, Spam, DoS, Virus, 
                               DNSBlacklist are main example threat types. Other kind of information is default ignored.
                               
 
        threat_name          : Name of the given threat. It is optional. Threat name can be the name of any malware,
                               botnet or other type of threats indicated in threat_type variable. Example threat names 
                               can be seen below. 
                               example threat_name : "Spyeye"
                               example threat_name : "Fake-AV"

        output_type          : Type of the given list information provided by that source. output_type must be a number 
                               between 1-3. Meaning of the numbers can be seen below.

                                   1 : IP List
                                   2 : Domain List
                                   3 : Port List

        output               : The list of the output_type information. If you set output_type as 1 you must provide
                               an IP List and so on for other options.
                               Examples of output can be seen below.
    
                               example IP List output: ['109.235.251.49 109.235.251.51 109.235.251.54 109.235.251.57 178.238.227.10']
    
                               example Domain List output: ['0o0o0o0o0.com 19js810300z.com 1efmdfieha-mff.com 1iii1i11i1ii.com 1zabslwvn538n4i5tcjl.com']
    
                               example Port List output: ['58470 58443 58439 58431 58427 58419 58417 58411 58398 58389']
    
    
        creation_time        : Time of the query creation.
                               example creation_time : "01.04.2011"
    
    '''
    
    def __init__(self, source_name, source_desc, source_link, threat_type, threat_name, output_type, output, creation_time):
        '''
            Assign initial values of the query.
        '''
        if (not (4>output_type>0)):
            sys.exit('output_type must be between 1-3, please look at the definition.\n')
        self.source_name = source_name
        self.source_desc = source_desc
        self.source_link = source_link
        self.threat_type = threat_type
        self.threat_name = threat_name
        self.output_type = output_type
        self.output = output
        self.creation_time = creation_time

    def insert_query(self):
        '''
            Insert query information to database according to its output type.
        '''
        #print self.output_type
        if self.output_type is 1:
            self.insert_ip_query()
        elif self.output_type is 2:
            self.insert_domain_query()
        elif self.output_type is 3:
            self.insert_port_query()
        else:
            sys.exit('output_type is wrong! Check the code!\n')

    def insert_ip_query(self):
        '''
            Insert ip query to database.
        '''
        

    def insert_domain_query(self):
        '''
            Insert domain query to database.
        '''
        pass

    def insert_port_query(self):
        '''
            Insert port query to database.
        '''
        pass

    def print_content(self):
        '''
            Print content of the query attributes.
        ''' 
        print self.source_name + self.source_desc + self.source_link + self.threat_type + str(self.threat_name) + str(self.output_type) + self.output + self.creation_time + '\n'







