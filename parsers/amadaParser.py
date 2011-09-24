#!/usr/local/bin/python

# Malware Database (AMaDa) :: AMaDa Blocklist Parser

from datetime import date
import os
import sys 
sys.path.append("..")

# nfquery modules
from querygenerator import create_query

nfquery = "/usr/local/nfquery/"
sourcepath = nfquery + "sources/amada/"
outputpath = nfquery + "outputs/amada/"

def fetch_source(source_link):
    os.system("fetch -o " + sourcepath + __file__ + " " + source_link)

def parse_source(sec_sourcefile):
    '''
     Amada gives information in two columns like that 
     ------------------------------------------------ 
     amada.output file
     ------------------------------------------------ 
     AMaDa IP Domain Blocklist                        
     Provided by abuse.ch Malware Database (AMaDa)    
     ~ http://amada.abuse.ch                          
                                                      
     IP address | Malware name                        
     109.235.251.49 # Fake-AV                         
     109.235.251.51 # Fake-AV                         
     ------------------------------------------------ 
     so parser parses the file after the 5th line
    '''

    source_file = open(sec_sourcefile,"r")
    source_desc = "Amada C&C IP Blocklist"
    today=date.today().isoformat()
    parsed_info={}
   
    # parse the file line by line and create a dictionary
    # for passing threat_name and output information to
    # createQuery() function.
    for line in source_file.readlines()[5:]:
        ip_address = line.split(" ")[0]
        threat_name = line.split(" ")[2].split("\n")[0]
        if (threat_name in parsed_info.keys()):
            parsed_info[threat_name] = parsed_info[threat_name] + " " + ip_address
        else:
            parsed_info[threat_name] = ip_address

    # threat_types = {'Botnet':'', 'Malware':'', 'Spam':'', 'DoS':'', 'Virus':''} but we only 
    # have botnet so we don;t need  another for loop  

    # output_type=1 means we give an ip list 
    for threat_name, ip_address in parsed_info.items():
        create_query(source_name, source_desc, source_link, "Botnet", threat_name, 1, ip_address, today)



    #def createOutput(source_name):
    #    today=date.today().isoformat()
    #    source=source_name
    #    port="-"
    #    MalOutput=open(outputpath + "MalOutput.amada","w")
    #    alignment="%-*s%-*s%-*s%-*s%*s"
    #    column1_width=20
    #    column2_width=20
    #    column3_width=15
    #    column4_width=15
    #    column5_width=15
    #    MalOutput.write(alignment % (column1_width, "MalType", column2_width, "MalIPaddress", column3_width, "Port", column4_width, "Source", column5_width, "Date\n"))
    #    for mal_name, mal_ipaddr in blocklist.items():
    #        for each_ip in mal_ipaddr.split(" "):
    #            print alignment % (column1_width, mal_name, column2_width, each_ip, column3_width, port, column4_width, source, column5_width, today) 
    #            MalOutput.write( alignment % (column1_width, mal_name, column2_width, each_ip, column3_width, port, column4_width, source, column5_width, today+"\n"))
    #    MalOutput.close()




''' 
    source_name should be registered to Query Server before using its parser.
'''
source_name = "Amada"
source_link = "http://amada.abuse.ch/blocklist.php?download=ipblocklist"
source_file = sourcepath + "blocklist"


#fetch_source(source_link)
parse_source(source_file)



