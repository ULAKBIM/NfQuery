#!/usr/local/bin/python

import simplejson 
import MySQLdb

# nfquery imports
from query import Query

def connectDB():
    # Open database connection
    db = MySQLdb.connect("localhost","nfquery","nf1!","ulaknet" )
    db = connectDB()
    cursor = db.cursor()
    # Fetch a single row using fetchone() method.
                                                  
    cursor.close()    
    db.close()
    # return db object for using outside 
    #return db
    
#q=Query(1, "amada", "FAKE-AV", "27.03.1990", ip="193.140.94.94").__dict__
#queryfile = open('outputs/test.jason', mode='w')
#queryfile.writelines(simplejson.dumps(q, indent=4)+"\n")
#queryfile.write(simplejson.dumps(q, indent=4))
#queryfile.write(simplejson.dumps(q, indent=4))
#queryfile.close()
#
#anotherfile=open('test.jason', mode='r')

#loaded = simplejson.load(anotherfile)
#print loaded




def createQuery(query_type, source_name, source_link, threat_type, threat_name_and_iplist, creation_time):
    '''
        A parser which parses malicious information from its security source uses this function to give one of the 
        ip, domain or port information to Query Generator. The parser must give the mandatory parameters of the
        function, and parameters must be given in the specified format as described below.
        
            source_name     : Name of the security source
                              example source_name : "Amada"

            source_link     : Download link of the security source
                              example source_link : "http://amada.abuse.ch/blocklist.php?download=ipblocklist" 

            threat_type     : Type of the given threat name. It must be one of the 
                              threat types which are published in nfquery website.
                              example threat_type : "Malware" 
                              example threat_type : "Botnet" 

            query_type      : Type of the query. It indicates what kind of data is gathered from the source.
                              query_type must be a number between 1-3. Meaning of the numbers can be seen
                              below.
                                                1 : IP List 
                                                2 : Domain List
                                                3 : Port List

            threat_info     : threat_info is a python dictionary which indicates the threat name and its parsed
                              data in key:value format. Threat name can be the name of any malware or botnet,
                              but parsed data must be a list of a query_type. So it could be one of the query_types
                              which are IP List, Domain List or Port List. Examples of threat info can be seen 
                              below.
                               
                              example threat_info with its IP List:  
                              {
                               'Win32.Scar': '91.188.60.4 91.188.60.5', 
                               'DDoS.Optima': '91.193.192.95', 
                               'Rootkit.Sirefef': '213.174.130.34 88.208.21.219 91.188.60.83 94.75.199.163', 
                               'Fake-AV': '109.235.251.49 109.235.251.51 109.235.251.54 109.235.251.57 178.238.227.10'
                              }

                              example threat_info with its domain List:
                              {
                                
                              }
                              example threat_info with its port List:
                              

            
            creation_time   : Time of the query creation.
                              example creation_time : "01.04.2011"

    '''
    output = parser_output
    query = Query()
    for threat_name, ip_address in output.items():
        #query.source_name = source_name
        query.source_name = "Amada"
        query.threat_type = threat_type
        #query.threat_desc = threat_desc
        query.threat_desc = threat_type + " description "
        query.creation_time = creation_time 
        query.ip = ip_address
        print threat_type + "  " + ip_address + "\n"
    if (query.ip is None):
        print 'boyle olmaz'
    else:
        print 'eyv'


def insertIpQuery():
def insertDomainQuery():
def insertPortQuery():



#def createDomainQuery():
#def createPortQuery():
#
#def enerateQuery(query):
    
    
    
            
        
        

        
        


#q = Query("a","b","c","d",ip="192.168.7.6")
#generateQuery(q)
        


    
    
    
        




















